# import cv2

class JS:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'
    }
    @classmethod
    def alert(cls, msg, url=''):
        if url:
            return "<script>" \
                    "alert('" + msg + "');" \
                    "window.location.href='" + url + "'" \
                "</script>"
        else:
            return "<script>" \
                    "alert('" + msg + "');" \
                    "window.history.back();" \
                "</script>"
    # @classmethod
    # def readFinger(cls, img1, img2):
    #     finger1 = cv2.imread(img1, 0)  # 0表示以灰度模式读取
    #     finger2 = cv2.imread(img2, 0)
    #     _, finger1 = cv2.threshold(finger1, 100, 255, cv2.THRESH_BINARY)
    #     _, finger2 = cv2.threshold(finger2, 100, 255, cv2.THRESH_BINARY)
    #     orb = cv2.ORB_create()
    #     key1, descriptors1 = orb.detectAndCompute(finger1, None)
    #     key2, descriptors2 = orb.detectAndCompute(finger2, None)
    #     bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    #     matches = bf.match(descriptors1, descriptors2)
    #     if len(matches) > 300:  # 设置一个阈值
    #         title = 'match'
    #         alert = '指纹匹配'
    #     else:
    #         title = 'no match'
    #         alert = '指纹不匹配'
    #     image = cv2.drawMatches(finger1, key1, finger2, key2, matches, None)
    #     cv2.imwrite('result.jpg', image)
    #     # cv2.imshow(title, image)
    #     # cv2.waitKey(0)
    #     # cv2.destroyAllWindows()
    #     return alert