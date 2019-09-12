import os

class ARCHCortexA():
    def __init__(self, **kwargs):
        Toolchain = kwargs.get('Toolchain', 'gcc')
        BUILD = kwargs.get('BUILD', 'debug')
        EXEC_PATH = kwargs.get('EXEC_PATH', 'NULL')
        USR_ROOT = kwargs.get('USR_ROOT', '/')

        if Toolchain == 'gcc':
            self.PREFIX = 'arm-linux-musleabi-'
            self.CC = self.PREFIX + 'gcc'
            self.CXX = self.PREFIX + 'g++'
            self.AS = self.PREFIX + 'gcc'
            self.AR = self.PREFIX + 'ar'
            self.LINK = self.PREFIX + 'gcc'
            self.TARGET_EXT = 'elf'
            self.SIZE = self.PREFIX + 'size'
            self.OBJDUMP = self.PREFIX + 'objdump'
            self.OBJCPY = self.PREFIX + 'objcopy'
            self.STRIP = self.PREFIX + 'strip'
            self.EXEC_PATH = EXEC_PATH

            DEVICE = ' -march=armv7-a -marm -msoft-float -n -pie -fpic --static'
            self.CFLAGS = DEVICE + ' -Wall'
            self.AFLAGS = ' -c' + DEVICE + ' -x assembler-with-cpp -D__ASSEMBLY__ -I.'
            LINK_SCRIPT = os.path.join(USR_ROOT, 'sdk', 'crt', 'gcc', 'arch', 'arm', 'gcc_arm.ld')
            self.LFLAGS = DEVICE + ' -Wl,--gc-sections,-Map=rtthread.map,-cref'+\
                            ' -T %s' % LINK_SCRIPT

            # generate debug info in all cases
            self.AFLAGS += ' -gdwarf-2'
            self.CFLAGS += ' -g -gdwarf-2'

            if BUILD == 'debug':
                self.CFLAGS += ' -O0'
            else:
                self.CFLAGS += ' -O2'

            self.CXXFLAGS = self.CFLAGS + ' -Woverloaded-virtual -fno-exceptions -fno-rtti'
        else:
            print('unsupport toolchain')
            exit(-1)

if __name__ == '__main__':
    arch = ARCHCortexA(Toochain = 'gcc')
    print(arch.CC)
