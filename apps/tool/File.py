class MyFile(object):
    def __init__(self,filename,mode):
        if 'b' in mode or 'html' in filename:
            if 'b' not in mode:
                mode += 'b'
            self.f = open(filename,mode)
        else:
            self.f=open(filename,mode,encoding='utf-8')



    def __enter__(self):

        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f.close()

    def __call__(self, *args, **kwargs):

        return self.f


class Writer(MyFile):
    def __init__(self, filename, mode='w'):

        super().__init__(filename, mode)


class Reader(MyFile):
    def __init__(self,filename,mode='r'):
        super().__init__(filename,mode)
