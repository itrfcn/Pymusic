// 当DOM内容加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 加载用户歌单列表
    loadUserPlaylists();
    
    // 添加歌单项点击事件委托
    document.addEventListener('click', function(e) {
        // 检查是否点击了歌单项链接
        const playlistLink = e.target.closest('.playlist-nav-link');
        if (playlistLink) {
            e.preventDefault();
            const playlistId = playlistLink.getAttribute('data-playlist-id');
            if (playlistId) {
                // 添加高亮样式
                document.querySelectorAll('.sidebar li').forEach(li => li.classList.remove('active'));
                playlistLink.closest('li').classList.add('active');
            }
        }
    });
    
    // 获取用户歌单列表的函数
    function loadUserPlaylists() {
        const playlistsContainer = document.getElementById('user-playlists');
        if (!playlistsContainer) return;
        
        fetch('/user/playlists')
            .then(response => {
                if (!response.ok) {
                    throw new Error('获取歌单失败');
                }
                return response.json();
            })
            .then(data => {
                // 清空加载提示
                playlistsContainer.innerHTML = '';
                
                if (data.playlists && data.playlists.length > 0) {
                    // 渲染歌单列表
                    data.playlists.forEach(playlist => {
                        const li = document.createElement('li');
                        li.className = 'playlist-item';
                        
                        // 检查是否存在有效的cover_url数据
                        let coverElement = '';
                        if (playlist.cover_url && playlist.cover_url.trim()) { // 更宽松的验证，只检查非空和非空白字符串
                            try {

                                let imgSrc = '';
                                const coverUrl = playlist.cover_url;
                                
                                // 更精确的base64图片处理逻辑
                                if (coverUrl.startsWith('data:image')) {
                                    // 已经是完整的Data URL格式
                                    imgSrc = coverUrl;
                                } else if (coverUrl.startsWith('http')) {
                                    // 是网络图片URL
                                    imgSrc = coverUrl;
                                } else {
                                    // 尝试识别为base64字符串并添加适当的前缀
                                    // 标准的base64字符串不应包含空格，且通常由A-Za-z0-9+/=组成
                                    const cleanBase64 = coverUrl.trim();
                                    if (/^[A-Za-z0-9+/=]+$/.test(cleanBase64) && cleanBase64.length > 10) {
                                        // 尝试根据文件头特征判断图片类型
                                        const mimeType = cleanBase64.startsWith('/9j/') ? 'image/jpeg' : 'image/png';
                                        imgSrc = `data:${mimeType};base64,${cleanBase64}`;

                                    } else {
                                        // 不是有效的base64，使用默认图片
                                        imgSrc = '/static/img/logo.png';

                                    }
                                }
                                
                                // 安全地使用封面图，如果加载失败显示默认图标
                                coverElement = `<img src="${imgSrc}" class="playlist-cover-img" alt="${playlist.name}" style="width: 24px; height: 24px; object-fit: cover; border-radius: 4px; margin-right: 8px; display: inline-block !important; vertical-align: middle;" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline-block';" />`;
                            } catch (e) {

                                // 出错时使用默认封面
                                coverElement = `<img src="/static/img/logo.png" class="playlist-cover-img" alt="${playlist.name}" />`;
                            }
                        } else {
                            // 没有封面URL时使用默认图标
                            
                            coverElement = ''; // 保持为空，这样默认图标会显示
                        }
                        
                        // 构建HTML内容，包含封面图和默认图标（作为后备）
                        li.innerHTML = `
                            <a class="nav-link playlist-nav-link" data-playlist-id="${playlist.id}">
                                ${coverElement}
                                <i class="fa-solid fa-music" ${coverElement ? 'style="display: none;"' : ''}></i>
                                <span class="playlist-name">${playlist.name}</span>
                                <span class="playlist-count">${playlist.song_count}首</span>
                            </a>
                        `;
                        
                        playlistsContainer.appendChild(li);
                        
                        // 点击歌单导航链接时触发
                        const playlistLink = li.querySelector('.playlist-nav-link');
                        playlistLink.addEventListener('click', function(e) {
                            e.preventDefault();
                            const playlistId = this.getAttribute('data-playlist-id');
                            navigateToPlaylistDetail(playlistId);
                        });
                    });
                } else {
                    // 显示没有歌单的提示
                    const emptyLi = document.createElement('li');
                    emptyLi.className = 'no-playlists';
                    emptyLi.innerHTML = '<span>暂无歌单</span>';
                    playlistsContainer.appendChild(emptyLi);
                }
            })
            .catch(error => {
    
                playlistsContainer.innerHTML = '<li class="error-message">加载失败，请刷新页面重试</li>';
            });
    }
    
    // 安全地暴露给window对象，避免与其他脚本冲突
    if (!window.updateSidebarPlaylist) {
        window.updateSidebarPlaylist = function(playlistId, newName) {
            loadUserPlaylists();
        };
    }
    // 创建音频对象用于播放音乐
    const audio = document.createElement('audio');
    audio.id = 'audio-player';
    document.body.appendChild(audio);
    // 存储当前播放列表，设置为全局变量以便其他模块访问
    window.currentPlaylist = [];
    // 当前播放歌曲的索引
    let currentTrackIndex = 0;
    // 存储歌词数据
    let lyrics = [];
    // 存储翻译歌词数据
    let tlyrics = [];
    // 控制歌词面板是否可见
    let lyricsVisible = false;
    // 标记是否正在拖拽进度条
    let isSeeking = false;
    // 标记是否正在调整音量
    let isAdjustingVolume = false;

    // 获取DOM元素
    // 播放/暂停按钮
    const playPauseBtn = document.querySelector('.play-pause-btn');
    // 进度条
    const progressBar = document.querySelector('.progress');
    // 进度条容器
    const progressContainer = document.querySelector('.progress-container');
    // 当前播放时间显示
    const currentTimeEl = document.querySelector('.progress-bar .time:first-child');
    // 总时长显示
    const durationEl = document.querySelector('.progress-bar .time:last-child');
    // 歌曲标题
    const songTitleEl = document.querySelector('.song-details h3');
    // 歌手信息
    const songArtistEl = document.querySelector('.song-details p');
    // 专辑封面图片
    const albumArtEl = document.querySelector('.song-info img');
    // 下一首按钮
    const nextBtn = document.querySelector('.control-buttons .fa-forward-step').parentElement;
    // 上一首按钮
    const prevBtn = document.querySelector('.control-buttons .fa-backward-step').parentElement;
    // 音量滑块
    const volumeSlider = document.querySelector('.volume-slider');
    // 音量滑块容器
    const volumeSliderContainer = document.querySelector('.volume-slider-container');
    // 音量按钮
    const volumeBtn = document.querySelector('.volume-control .btn');
    // 获取主内容区域
    const mainContent = document.querySelector('.main-content');
    // 搜索输入框
    const searchInput = document.querySelector('.search-bar input');
    // 播放器选项区域
    const playerOptions = document.querySelector('.player-options');

    // 获取歌词和播放列表切换按钮
    // 歌词切换按钮
    const lyricsToggleBtn = document.querySelector('.btn-lyrics-toggle');
    // 播放列表切换按钮
    const playlistToggleBtn = document.querySelector('.player-options .fa-list').parentElement;

    // 创建歌词面板元素
    const lyricsPanel = document.createElement('div');
    // 设置歌词面板类名和初始状态
    lyricsPanel.className = 'lyrics-panel hidden';
    // 设置歌词面板HTML内容
    lyricsPanel.innerHTML = `
           <div class="lyrics-header">
               <span>歌词</span>
               <button class="btn btn-close-lyrics"><i class="fa-solid fa-xmark"></i></button>
                 </div>
           <ul class="lyrics-lines"></ul>
       `;
    // 将歌词面板添加到主视图中
    document.querySelector('.main-view').appendChild(lyricsPanel);

    // 创建播放列表面板元素
    const playlistPanel = document.createElement('div');
    // 设置播放列表面板类名和初始状态
    playlistPanel.className = 'playlist-panel hidden';
    // 设置播放列表面板HTML内容
    playlistPanel.innerHTML = `
           <div class="playlist-header">
               <span>当前播放列表</span>
               <button class="btn btn-close-playlist"><i class="fa-solid fa-xmark"></i></button>
           </div>
           <ul class="playlist-lines"></ul>
       `;
    // 将播放列表面板添加到主视图中
    document.querySelector('.main-view').appendChild(playlistPanel);

    // 导航到歌单详情（避免与playlist_detail.html中的loadPlaylistDetail冲突）
    function navigateToPlaylistDetail(playlistId) {
        // 使用loadPage函数加载歌单详情页面
        loadPage(`playlist_detail`, false); 
        // 确保播放列表详情加载完成后，更新URL
        const url = `/playlist_detail?id=${playlistId}`;
        window.history.pushState({ path: url }, '', url);
    }
    // --- SPA Navigation ---
    // 加载页面函数
    function loadPage(url, pushState = true) {
        // 直接使用index路由格式，确保与Flask路由匹配
        let pageName;
        if (url === '/') {
            pageName = 'discover';
        } else if (url.startsWith('/')) {
            pageName = url.substring(1); // 去掉开头的/
        } else {
            pageName = url;
        }  

        // 构建正确的index URL格式
        const indexUrl = `/index/${pageName}`;

        // 发起fetch请求获取页面内容
        fetch(indexUrl)
            .then(response => {
                // 检查响应是否成功
                if (!response.ok) {
                    throw new Error(`网络请求失败: ${response.status} ${response.statusText}`);
                }
                // 返回响应文本
                return response.text();
            })
            .then(html => {
                // 确保mainContent元素存在
                if (!mainContent) {
                    return;
                }
                
                // 替换主内容区域的内容
                mainContent.innerHTML = html;

                // 执行加载的partial中的脚本
                executeEmbeddedScripts(mainContent);

                // 如果需要更新浏览器历史记录
                if (pushState) {
                    window.history.pushState({ path: url }, '', url);
                }

                // 根据页面URL调用特定页面的初始化函数
                if (pageName === 'my-music') {
                    // 给页面内容一些渲染时间
                    setTimeout(() => {
                        if (window.initMyMusicPage) {
                            window.initMyMusicPage();
                        }
                    }, 100);
                }
                // 为历史页面添加初始化逻辑
                if (pageName === 'history') {
                    setTimeout(() => {
                        if (window.initHistoryPage) {
                            window.initHistoryPage();
                        }
                    }, 100);
                }
            })
            .catch(error => {
                // 处理加载错误
    
                mainContent.innerHTML = `<p>加载内容时出错: ${error.message}. 请重试。</p>`;
            });
      }

    // 执行动态加载的子页面内容中的<script>标签
    function executeEmbeddedScripts(container) {
        // 清理之前注入的动态脚本以避免重复
        document.querySelectorAll('script[data-dynamic-script="true"]').forEach(s => s.remove());

        // 获取所有脚本标签
        const scripts = container.querySelectorAll('script');
        scripts.forEach(orig => {
            // 创建新的脚本元素
            const newScript = document.createElement('script');
            // 保留原有的属性
            for (const attr of orig.attributes) {
                newScript.setAttribute(attr.name, attr.value);
            }
            // 设置动态脚本标识
            newScript.setAttribute('data-dynamic-script', 'true');

            // 如果是外部脚本
            if (orig.src) {
                newScript.src = orig.src;
                document.body.appendChild(newScript);
                return;
            }

            // 获取脚本内容
            let code = orig.textContent || '';

            // 将DOMContentLoaded包装的代码转换为立即执行函数
            // 匹配: document.addEventListener('DOMContentLoaded', function () { ... });
            const dclPattern1 = /document\.addEventListener\(["']DOMContentLoaded["']\s*,\s*function\s*\(\)\s*\{/;
            const dclPattern2 = /document\.addEventListener\(["']DOMContentLoaded["']\s*,\s*\(\)\s*=>\s*\{/;
            if (dclPattern1.test(code) || dclPattern2.test(code)) {
                code = code
                    .replace(dclPattern1, '(function(){')
                    .replace(dclPattern2, '(function(){')
                    .replace(/\}\);\s*$/, '})();');
            }

            // 设置脚本内容
            newScript.textContent = code;
            // 添加到body中执行
            document.body.appendChild(newScript);
        });
    }
    

    // 简化的导航链接点击事件处理
    const navLinks = document.querySelectorAll('a.nav-link');
    
    navLinks.forEach((link) => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const url = this.getAttribute('href');
            
            if (url && url !== '#') {
                // 移除所有活动状态
                document.querySelectorAll('.sidebar .menu ul li').forEach(li => {
                    li.classList.remove('active');
                });
                
                // 添加当前活动状态
                const parentLi = this.closest('li');
                if (parentLi) {
                    parentLi.classList.add('active');
                }
                
                // 调用loadPage函数
                if (typeof loadPage === 'function') {
                    loadPage(url);
                }
            }
        });
    });

    // 浏览器后退/前进事件处理
    window.addEventListener('popstate', function (event) {
        // 如果有历史状态则加载对应页面
        if (event.state && event.state.path) {
            loadPage(event.state.path, false);
        } else {
            // 处理初始页面加载情况
            loadPage(location.pathname, false);
        }
    });


    // Helpers: LRC歌词解析和渲染
    // 解析LRC歌词格式
    function parseLRC(text) {
        // 存储解析后的歌词行
        const lines = [];
        // 如果没有歌词文本则返回空数组
        if (!text) return lines;
        // 按行分割歌词文本
        text.split(/\r?\n/).forEach(line => {
            // 匹配时间标签
            const matches = [...line.matchAll(/\[(\d{1,2}):(\d{1,2})(?:\.(\d{1,3}))?\]/g)];
            // 提取歌词内容（去除时间标签）
            const content = line.replace(/\[.*?\]/g, '').trim();
            // 处理每个时间标签
            matches.forEach(m => {
                // 解析分钟
                const min = parseInt(m[1], 10);
                // 解析秒数
                const sec = parseInt(m[2], 10);
                // 解析毫秒
                const ms = m[3] ? parseInt(m[3].padEnd(3, '0'), 10) : 0;
                // 计算总时间（秒）
                const time = min * 60 + sec + ms / 1000;
                // 添加到歌词行数组
                lines.push({ time, text: content });
            });
        });
        // 按时间排序
        return lines.sort((a, b) => a.time - b.time);
    }

    // 按时间配对歌词和翻译歌词
    function pairLyricsByTime(lrcLines, tlLines) {
        // 存储配对结果
        const paired = [];
        // 翻译歌词索引
        let j = 0;
        // 遍历原始歌词
        for (let i = 0; i < lrcLines.length; i++) {
            const l = lrcLines[i];
            // 初始化翻译歌词匹配项
            let tMatch = null;
            // 查找匹配的翻译歌词
            while (j < tlLines.length && tlLines[j].time <= l.time + 0.5) {
                // 如果时间差在0.5秒内则认为是匹配的
                if (Math.abs(tlLines[j].time - l.time) <= 0.5) {
                    tMatch = tlLines[j];
                    break;
                }
                j++;
            }
            // 添加配对结果
            paired.push({ lrc: l, tlyric: tMatch });
        }
        return paired;
    }

    // 渲染歌词
    function renderLyrics() {
        // 获取歌词行容器
        const ul = lyricsPanel.querySelector('.lyrics-lines');
        // 清空现有内容
        ul.innerHTML = '';
        // 配对歌词和翻译歌词
        const paired = pairLyricsByTime(lyrics, tlyrics);
        // 遍配对结果渲染每一行
        paired.forEach(({ lrc, tlyric }) => {
            // 创建歌词行元素
            const li = document.createElement('li');
            // 设置类名
            li.className = 'lyrics-line';
            // 设置HTML内容
            li.innerHTML = `
                <div class="lrc">${lrc ? lrc.text : ''}</div>
                <div class="tlyric">${tlyric ? tlyric.text : ''}</div>
            `;
            // 添加到容器中
            ul.appendChild(li);
        });
    }

    // 更新歌词高亮显示
    function updateLyricsHighlight(currentTime) {
        // 获取歌词行容器
        const ul = lyricsPanel.querySelector('.lyrics-lines');
        // 如果没有歌词行则返回
        if (!ul.children.length) return;
        // 当前激活的歌词索引
        let activeIndex = -1;
        // 查找当前应该高亮的歌词行
        for (let i = 0; i < lyrics.length; i++) {
            if (currentTime >= lyrics[i].time) {
                activeIndex = i;
            } else {
                break;
            }
        }
        // 更新所有歌词行的激活状态
        [...ul.children].forEach((li, idx) => {
            if (idx === activeIndex) {
                li.classList.add('active');
            } else {
                li.classList.remove('active');
            }
        });
        // 自动滚动以保持激活行居中
        if (activeIndex >= 0) {
            const activeEl = ul.children[activeIndex];
            const panelHeight = lyricsPanel.clientHeight;
            const offsetTop = activeEl.offsetTop - panelHeight / 2 + activeEl.clientHeight / 2;
            lyricsPanel.scrollTo({ top: offsetTop, behavior: 'smooth' });
        }
    }

    // --- Player Logic ---
    // 防抖函数
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // 最近播放的歌曲ID缓存
    let lastPlayedSongId = null;
    let lastSaveTime = 0;
    
    // 保存播放历史（添加防抖处理）
    const debouncedSavePlayHistory = debounce(async function(songId) {
        // 检查是否已登录（通过检查用户信息显示区域）
        const userInfo = document.querySelector('.user-info');
        if (userInfo && userInfo.textContent.includes('登录')) {
            // 未登录，不保存历史记录
            return;
        }
        
        // 如果是同一首歌，限制保存频率为30秒
        const now = Date.now();
        if (songId === lastPlayedSongId && now - lastSaveTime < 30000) {
            
            return;
        }
        
        try {
            const response = await fetch('/user/save_history', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ song_id: songId })
            });
            
            // 更新最后播放信息
            lastPlayedSongId = songId;
            lastSaveTime = now;
            
            // 不处理响应，即使失败也不影响用户体验
        } catch (error) {

            // 静默失败，不提示用户
        }
    }, 1000); // 1秒防抖延迟
    
    // 保存播放历史的公共接口
    function savePlayHistory(songId) {
        debouncedSavePlayHistory(songId);
    }

    // 播放指定索引的歌曲
    function playTrack(trackIndex) {
        // 检查索引是否有效
        if (trackIndex < 0 || trackIndex >= window.currentPlaylist.length) {
    
            return;
        }
        // 更新当前播放索引
        currentTrackIndex = trackIndex;
        // 获取当前歌曲
        const track = window.currentPlaylist[currentTrackIndex];
        
        // 防御性检查：确保track.id存在且有效
        if (!track.id || track.id === 0 || track.id === '0' || track.id === undefined || track.id === null) {
    
            // 尝试从data属性获取ID
            const row = document.querySelector(`tr[data-song-id]`);
            if (row && row.dataset.songId) {
                track.id = parseInt(row.dataset.songId);
        
            } else {
                // 播放下一首
        
                nextTrack();
                return;
            }
        }
        
        // 保存播放历史
        savePlayHistory(track.id);
        // 设置歌曲ID到音频元素，供添加到歌单功能使用
        audio.dataset.songId = track.id;

        // 获取歌曲播放URL
        fetch(`/music/song/url/${track.id}`)
            .then(response => response.json())
            .then(data => {
                // 如果获取URL成功
                if (data.code === 200 && data.data.url) {
                    // 设置音频源
                    audio.src = data.data.url;
                    // 更新歌曲标题
                    songTitleEl.textContent = track.name;
                    // 更新歌手信息
                    songArtistEl.textContent = (track.artists || []).map(a => a.name).join(' / ');

                    // 获取歌曲封面
                    fetch(`/music/song/cover/${track.id}`)
                        .then(res => res.json())
                        .then(coverData => {
                            // 如果获取封面成功
                            if (coverData.code === 200) {
                                albumArtEl.src = coverData.data.picUrl;
                            } else {
                                // 使用默认封面
                                albumArtEl.src = 'https://picsum.photos/56/56?random=1';
                            }
                        })
                        .catch(() => {
                            // 出错时使用默认封面
                            albumArtEl.src = 'https://picsum.photos/56/56?random=1';
                        });

                    // 获取歌曲歌词
                    fetch(`/music/song/lyric/${track.id}`)
                        .then(r => r.json())
                        .then(ld => {
                            // 如果获取歌词成功
                            if (ld.code === 200 && ld.data) {
                                // 解析歌词和翻译歌词
                                lyrics = parseLRC(ld.data.lrc);
                                tlyrics = parseLRC(ld.data.tlyric);
                                // 渲染歌词
                                renderLyrics();
                            } else {
                                // 清空歌词
                                lyrics = [];
                                tlyrics = [];
                                renderLyrics();
                            }
                        })
                        .catch(() => {
                            // 出错时清空歌词
                            lyrics = [];
                            tlyrics = [];
                            renderLyrics();
                        });
                    // 播放音频
                    audio.play();
                    // 更新播放按钮图标
                    playPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
                    // 更新正在播放指示器
                    updateNowPlayingIndicator(track.id);
                } else {
                    // 获取URL失败时播放下一首
    
                    nextTrack();
                }
            })
            .catch(error => {
                // 出错时播放下一首
    
                nextTrack();
            });
    }

    // 添加防抖变量
    let playTrackDebounceTimer = null;
    
    // 防抖版本的playTrack函数
    const debouncedPlayTrack = function(trackIndex) {
        // 清除之前的定时器
        if (playTrackDebounceTimer) {
            clearTimeout(playTrackDebounceTimer);
        }
        
        // 设置新的定时器，300ms内的重复调用会被合并
        playTrackDebounceTimer = setTimeout(() => {
            playTrack(trackIndex);
        }, 300);
    };
    
    // 暴露到全局，供其他模块调用
    window.playTrack = debouncedPlayTrack;

    // 播放下一首
    function nextTrack() {
        // 直接调用原始函数
        playTrack((currentTrackIndex + 1) % window.currentPlaylist.length);
    }

    // 播放上一首
    function prevTrack() {
        // 直接调用原始函数
        playTrack((currentTrackIndex - 1 + window.currentPlaylist.length) % window.currentPlaylist.length);
    }

    // 恢复播放
    function resumePlay() {
        // 直接调用原始函数
        playTrack(currentTrackIndex);
    }

    // 切换播放/暂停状态
    function togglePlayPause() {
        // 如果当前是暂停状态
        if (audio.paused) {
            // 如果已有音频源则播放
            if (audio.src) {
                audio.play();
                playPauseBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
            } else if (currentPlaylist.length > 0) {
                // 否则播放当前歌曲
                playTrack(currentTrackIndex);
            }
        } else {
            // 暂停播放
            audio.pause();
            playPauseBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
        }
    }

    // 更新播放进度
    function updateProgress() {
        const { currentTime, duration } = audio;
        // 如果有总时长
        if (duration) {
            // 计算进度百分比
            const progressPercent = (currentTime / duration) * 100;
            // 更新进度条宽度
            progressBar.style.width = `${progressPercent}%`;
            // 更新时间显示
            currentTimeEl.textContent = formatTime(currentTime);
            durationEl.textContent = formatTime(duration);
            // 如果歌词可见则更新歌词高亮
            if (lyricsVisible) {
                updateLyricsHighlight(currentTime);
            }
        }
    }

    // 设置播放进度
    function setProgress(e) {
        // 获取进度条容器的边界信息
        const rect = progressContainer.getBoundingClientRect();
        // 计算点击位置的相对位置
        const posX = (e.clientX - rect.left) / rect.width;
        // 获取音频总时长
        const duration = audio.duration;
        // 如果有总时长则设置当前播放时间
        if (duration) {
            audio.currentTime = Math.min(Math.max(posX, 0), 1) * duration;
        }
    }

    // 格式化时间显示（秒转为分:秒格式）
    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${minutes}:${secs < 10 ? '0' : ''}${secs}`;
    }

    // 设置音量
    function setVolume(e) {
        // 获取音量滑块容器的边界信息
        const rect = volumeSliderContainer.getBoundingClientRect();
        // 计算点击位置的相对位置
        const posX = (e.clientX - rect.left) / rect.width;
        // 限制音量在0-1之间
        const volume = Math.min(Math.max(posX, 0), 1);
        // 设置音频音量
        audio.volume = volume;
        // 更新音量滑块显示
        volumeSlider.style.width = `${volume * 100}%`;
        // 更新音量图标
        updateVolumeIcon(volume);
    }

    // 更新音量图标
    function updateVolumeIcon(volume) {
        // 根据音量大小选择不同图标
        let iconClass = 'fa-volume-xmark';
        if (volume > 0.5) {
            iconClass = 'fa-volume-high';
        } else if (volume > 0) {
            iconClass = 'fa-volume-low';
        }

        // 更新音量按钮图标
        volumeBtn.innerHTML = `<i class="fa-solid ${iconClass}"></i>`;
    }

    // 切换静音状态
    function toggleMute() {
        // 切换静音状态
        audio.muted = !audio.muted;
        // 如果静音
        if (audio.muted) {
            // 隐藏音量滑块
            volumeSlider.style.width = '0%';
            updateVolumeIcon(0);
        } else {
            // 显示音量滑块
            volumeSlider.style.width = `${audio.volume * 100}%`;
            updateVolumeIcon(audio.volume);
        }
    }

    // 搜索音乐函数
    async function searchMusic(query) {
        try {
            // 发起搜索请求
            const response = await fetch(`/music/search?name=${encodeURIComponent(query)}&page=0`);
            const data = await response.json();
            // 如果搜索成功
            if (data.code === 200 && data.result && data.result.songs) {
                renderSearchResults(data.result.songs);
            } else {
                // 搜索失败处理

                mainContent.innerHTML = '<p class="error-message">未能找到任何结果。</p>';
            }
        } catch (error) {
            // 出错处理

            mainContent.innerHTML = '<p class="error-message">搜索时发生错误。</p>';
        }
    }

    // 渲染搜索结果
    function renderSearchResults(songs) {
        // 清空现有内容
        mainContent.innerHTML = '';
        // 创建歌曲列表
        const trackList = document.createElement('ul');
        trackList.className = 'track-list';

        // 遍历歌曲渲染每一项
        songs.forEach((song, index) => {
            const trackItem = document.createElement('li');
            trackItem.className = 'track-item';
            trackItem.dataset.trackId = song.id;
            trackItem.innerHTML = `
                <div class="track-number">${index + 1}</div>
                <div class="track-info">
                    <div class="track-name">${song.name}</div>
                    <div class="track-artist">${song.artists ? song.artists.map(a => a.name).join(' / ') : (song.ar ? song.ar.map(a => a.name).join(' / ') : '')}</div>
                </div>
                <div class="track-duration">${formatTime((song.duration || song.dt) / 1000)}</div>
            `;
            // 添加点击事件
            trackItem.addEventListener('click', () => {
                // 设置当前播放列表
                window.currentPlaylist = songs.map(s => ({
                    ...s,
                    // 标准化数据结构
                    album: s.album || s.al || { picUrl: 'https://picsum.photos/56/56?random=1' },
                    artists: s.artists || s.ar || []
                }));
                // 播放点击的歌曲
                playTrack(index);
            });
            trackList.appendChild(trackItem);
        });

        // 添加到主内容区域
        mainContent.appendChild(trackList);
    }

    // 加载歌单函数
    async function loadPlaylist(playlistId) {
        try {
            // 发起获取歌单请求
            const response = await fetch(`/music/playlist/${playlistId}`);
            const data = await response.json();

            // 如果获取成功
            if (data.code === 200 && data.result && data.result.tracks) {
                // 设置当前播放列表
                window.currentPlaylist = data.result.tracks;
                // 在主视图中渲染播放列表
                renderPlaylistInPanel(currentPlaylist);
                // 自动播放第一首
                playTrack(0);
            } else {
                // 失败处理

            }
        } catch (error) {
            // 出错处理

        }
    }

    // 在面板中渲染播放列表
    function renderPlaylistInPanel(tracks) {
        // 先设置全局播放列表
        window.currentPlaylist = tracks;
        // 创建歌曲列表
        const trackList = document.createElement('ul');
        trackList.className = 'track-list';

        // 遍历歌曲渲染每一项
        window.currentPlaylist.forEach((track, index) => {
            const trackItem = document.createElement('li');
            trackItem.className = 'track-item';
            trackItem.dataset.trackId = track.id;
            trackItem.innerHTML = `
                <div class="track-number">${index + 1}</div>
                <div class="track-info">
                    <div class="track-name">${track.name}</div>
                    <div class="track-artist">${(track.artists || []).map(a => a.name).join(' / ')}</div>
                </div>
                <div class="track-duration">${formatTime((track.duration || track.dt) / 1000)}</div>
            `;
            // 添加点击事件 - 使用防抖版本
            trackItem.addEventListener('click', () => {
                window.playTrack(index);
            });
            trackList.appendChild(trackItem);
        });

        // 清空主内容区域并添加歌曲列表
        mainContent.innerHTML = '';
        mainContent.appendChild(trackList);
    }


    // 更新正在播放指示器
    function updateNowPlayingIndicator(trackId) {
        // 更新主内容区域的播放指示器
        document.querySelectorAll('.track-item').forEach(item => {
            item.classList.remove('playing');
            if (item.dataset.trackId == trackId) {
                item.classList.add('playing');
            }
        });
        // 同时更新侧边栏播放列表面板
        const playlistPanelLines = playlistPanel.querySelectorAll('.playlist-line');
        playlistPanelLines.forEach((item, index) => {
            item.classList.remove('playing');
            if (window.currentPlaylist[index] && window.currentPlaylist[index].id == trackId) {
                item.classList.add('playing');
            }
        });
    }

    // --- Event Listeners ---
    // 播放/暂停按钮事件
    playPauseBtn.addEventListener('click', togglePlayPause);
    // 下一首按钮事件
    nextBtn.addEventListener('click', nextTrack);
    // 上一首按钮事件
    prevBtn.addEventListener('click', prevTrack);
    // 音频时间更新事件
    audio.addEventListener('timeupdate', updateProgress);
    // 音频播放结束事件
    audio.addEventListener('ended', nextTrack);

    // 进度条交互事件
    progressContainer.addEventListener('click', setProgress);
    progressContainer.addEventListener('mousedown', () => { isSeeking = true; });
    document.addEventListener('mousemove', (e) => { if (isSeeking) setProgress(e); });
    document.addEventListener('mouseup', () => { isSeeking = false; });
    // 音量滑块交互事件
    volumeSliderContainer.addEventListener('click', setVolume);
    volumeSliderContainer.addEventListener('mousedown', () => { isAdjustingVolume = true; });
    document.addEventListener('mousemove', (e) => { if (isAdjustingVolume) setVolume(e); });
    document.addEventListener('mouseup', () => { isAdjustingVolume = false; });
    // 音量按钮事件
    volumeBtn.addEventListener('click', toggleMute);
    // 搜索输入框回车事件
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                searchMusic(query);
            }
        }
    });

    // 歌词切换（歌词面板显示/隐藏）
    lyricsToggleBtn.addEventListener('click', () => {
        lyricsVisible = !lyricsVisible;
        lyricsPanel.classList.toggle('hidden', !lyricsVisible);
    });
    // 关闭歌词面板按钮事件
    lyricsPanel.querySelector('.btn-close-lyrics').addEventListener('click', () => {
        lyricsVisible = false;
        lyricsPanel.classList.add('hidden');
    });

    // 播放列表面板切换
    playlistToggleBtn.addEventListener('click', () => {
        const hidden = playlistPanel.classList.contains('hidden');
        if (hidden) {
            renderPlaylistSidePanel();
        }
        playlistPanel.classList.toggle('hidden');
    });
    // 关闭播放列表面板按钮事件
    playlistPanel.querySelector('.btn-close-playlist').addEventListener('click', () => {
        playlistPanel.classList.add('hidden');
    });

    // 渲染侧边栏播放列表面板
    function renderPlaylistSidePanel() {
        const ul = playlistPanel.querySelector('.playlist-lines');
        ul.innerHTML = '';
        window.currentPlaylist.forEach((track, index) => {
            const li = document.createElement('li');
            li.className = 'playlist-line';
            li.innerHTML = `
                <span class="idx">${index + 1}</span>
                <span class="name">${track.name}</span>
                <span class="artist">${(track.artists || []).map(a => a.name).join(' / ')}</span>
            `;
            // 如果是当前播放歌曲则添加playing类
            if (index === currentTrackIndex) li.classList.add('playing');
            // 添加点击事件 - 使用防抖版本
            li.addEventListener('click', () => window.playTrack(index));
            ul.appendChild(li);
        });
    }

    // 搜索防抖处理
    let searchDebounceTimer = null;
    searchInput.addEventListener('input', () => {
        const query = searchInput.value.trim();
        clearTimeout(searchDebounceTimer);
        if (!query) return;
        // 300ms防抖延迟
        searchDebounceTimer = setTimeout(() => searchMusic(query), 300);
    });

    // 添加播放器动画效果和响应式行为
    function addPlayerAnimations() {
        // 检测是否为移动设备
        const isMobile = window.innerWidth <= 480;
        
        // 为桌面设备添加悬停效果
        if (!isMobile) {
            // 进度条悬停效果
            progressContainer.addEventListener('mouseenter', function() {
                this.style.height = '8px';
            });

            progressContainer.addEventListener('mouseleave', function() {
                if (!isSeeking) {
                    this.style.height = '6px';
                }
            });

            // 音量控制悬停效果
            if (volumeSliderContainer) {
                volumeSliderContainer.addEventListener('mouseenter', function() {
                    this.style.height = '8px';
                });

                volumeSliderContainer.addEventListener('mouseleave', function() {
                    if (!isAdjustingVolume) {
                        this.style.height = '6px';
                    }
                });
            }
        }
        
        // 为移动设备添加触摸优化
        if (isMobile) {
            // 为进度条添加触摸支持
            progressContainer.addEventListener('touchstart', function() {
                isSeeking = true;
            });
            
            progressContainer.addEventListener('touchend', function() {
                isSeeking = false;
            });
            
            // 为音量控制添加触摸支持
            if (volumeSliderContainer) {
                volumeSliderContainer.addEventListener('touchstart', function() {
                    isAdjustingVolume = true;
                });
                
                volumeSliderContainer.addEventListener('touchend', function() {
                    isAdjustingVolume = false;
                });
            }
        }
        
        // 响应窗口大小变化
        window.addEventListener('resize', function() {
            // 根据当前窗口大小重新设置播放器样式
            updatePlayerLayout();
        });
    }
    
    // 更新播放器布局以适应不同屏幕尺寸
    function updatePlayerLayout() {
        const width = window.innerWidth;
        
        // 这里可以根据需要添加更多的响应式布局调整
        // 比如根据屏幕宽度调整元素大小、位置等
    }

    // 新增函数：从歌单播放歌曲
    window.playTrackFromPlaylist = function playTrackFromPlaylist(tracks, trackIndex) {
        // 设置当前播放列表
        window.currentPlaylist = tracks.map(track => ({
            ...track,
            // 标准化数据结构
            id: track.id || track.song_id || track.songid || track.idx || 0, // 确保id字段存在
            album: track.album || track.al || { picUrl: 'https://picsum.photos/56/56?random=1' },
            artists: track.artists || track.ar || []
        }));

        // 调用window.playTrack（防抖版本）以避免重复请求
        window.playTrack(trackIndex);

        // 更新播放列表面板
        renderPlaylistSidePanel();
    };

    // 歌单列表渲染函数
    window.renderPlaylist = function renderPlaylist(tracks) {
        // 优先查找wy-music-parser容器中的结果区域
        const resultContainer = document.querySelector('.wy-music-parser .result-container');
        // 如果找不到，再使用主内容区域作为后备
        const fallbackContainer = document.querySelector('.main-content');
        const container = resultContainer || fallbackContainer;
        
        if (!container) return;
        container.innerHTML = '';

        // 使用wy-music-parser容器内的样式隔离
        const trackListContainer = document.createElement('div');
        trackListContainer.className = 'wy-playlist-result';
        
        const trackList = document.createElement('div');
        trackList.className = 'tracks-container';
        
        const table = document.createElement('table');
        table.className = 'tracks-table';
        
        // 创建表头
        const thead = document.createElement('thead');
        thead.innerHTML = `
            <tr>
                <th class="col-index">序号</th>
                <th class="col-title">歌曲名</th>
                <th class="col-artist">歌手</th>
                <th class="col-album">专辑</th>
            </tr>
        `;
        table.appendChild(thead);
        
        // 创建表格主体
        const tbody = document.createElement('tbody');
        
        tracks.forEach((track, index) => {
            const row = document.createElement('tr');
            row.dataset.trackId = track.id;
            
            // 获取艺术家和专辑信息
            const artistNames = (track.artists || []).map(a => a.name || '未知艺术家').join(' / ');
            const albumName = (track.album && track.album.name) ? track.album.name : '未知专辑';
            
            row.innerHTML = `
                <td class="col-index">
                    <button class="track-play-button" title="播放">
                        <i class="fa-solid fa-play"></i>
                    </button>
                    <span>${index + 1}</span>
                </td>
                <td class="col-title">${track.name || '未知歌曲'}</td>
                <td class="col-artist">${artistNames}</td>
                <td class="col-album">${albumName}</td>
            `;
            
            // 添加播放按钮点击事件
            const playBtn = row.querySelector('.track-play-button');
            if (playBtn) {
                playBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    if (typeof window.playTrack === 'function') {
                        window.playTrack(index);
                    }
                });
            }
            
            // 添加整行点击事件
            row.addEventListener('click', () => {
                if (typeof window.playTrack === 'function') {
                    window.playTrack(index);
                }
            });
            
            tbody.appendChild(row);
        });
        
        table.appendChild(tbody);
        trackList.appendChild(table);
        trackListContainer.appendChild(trackList);
        container.appendChild(trackListContainer);
    };

    // --- Initialization ---
    // 添加播放器动画
    addPlayerAnimations();
});
