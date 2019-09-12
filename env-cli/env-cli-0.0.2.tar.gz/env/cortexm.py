import os

class ARCHCortexM():
    def __init__(self, **kwargs):
        Toolchain = kwargs.get('Toolchain', 'gcc')
        BUILD = kwargs.get('BUILD', 'debug')

        if Toolchain == 'gcc':
            self.PREFIX = 'arm-none-eabi-'
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

            DEVICE = ' -mcpu=cortex-m4 -mthumb -mfpu=fpv4-sp-d16 -mfloat-abi=hard -ffunction-sections -fdata-sections'
            self.CFLAGS = DEVICE + ' -Dgcc'
            self.AFLAGS = ' -c' + DEVICE + ' -x assembler-with-cpp -Wa,-mimplicit-it=thumb '
            LINK_SCRIPT = 'board/linker_scripts/link.lds'
            self.LFLAGS = DEVICE + ' -Wl,--gc-sections,-Map=rtthread.map,-cref,-u,Reset_Handler -T ' + LINK_SCRIPT

            if BUILD == 'debug':
                self.CFLAGS += ' -O0 -gdwarf-2 -g'
                self.AFLAGS += ' -gdwarf-2'
            else:
                self.CFLAGS += ' -O2'

            self.CXXFLAGS = self.CFLAGS + ' -Woverloaded-virtual -fno-exceptions -fno-rtti'

        if Toolchain == 'keil':
            self.CC = 'armcc'
            self.CXX = 'armcc'
            self.AS = 'armasm'
            self.AR = 'armar'
            self.LINK = 'armlink'
            self.TARGET_EXT = 'axf'

            DEVICE = ' --cpu Cortex-M4.fp '
            self.CFLAGS = '-c ' + DEVICE + ' --apcs=interwork --c99'
            self.AFLAGS = DEVICE + ' --apcs=interwork '
            self.LFLAGS = DEVICE + ' --scatter "board\linker_scripts\link.sct" --info sizes --info totals --info unused --info veneers --list rtthread.map --strict'
            self.CFLAGS += ' -I' + EXEC_PATH + '/ARM/ARMCC/include'
            self.LFLAGS += ' --libpath=' + EXEC_PATH + '/ARM/ARMCC/lib'

            self.CFLAGS += ' -D__MICROLIB '
            self.AFLAGS += ' --pd "__MICROLIB SETA 1" '
            self.LFLAGS += ' --library_type=microlib '
            self.EXEC_PATH += '/ARM/ARMCC/bin/'

            if BUILD == 'debug':
                self.CFLAGS += ' -g -O0'
                self.AFLAGS += ' -g'
            else:
                self.CFLAGS += ' -O2'

            self.CXXFLAGS = self.CFLAGS 

        if Toolchain == 'iar':
            self.CC = 'iccarm'
            self.CXX = 'iccarm'
            self.AS = 'iasmarm'
            self.AR = 'iarchive'
            self.LINK = 'ilinkarm'
            self.TARGET_EXT = 'out'

            DEVICE = '-Dewarm'

            self.CFLAGS = DEVICE
            self.CFLAGS += ' --diag_suppress Pa050'
            self.CFLAGS += ' --no_cse'
            self.CFLAGS += ' --no_unroll'
            self.CFLAGS += ' --no_inline'
            self.CFLAGS += ' --no_code_motion'
            self.CFLAGS += ' --no_tbaa'
            self.CFLAGS += ' --no_clustering'
            self.CFLAGS += ' --no_scheduling'
            self.CFLAGS += ' --endian=little'
            self.CFLAGS += ' --cpu=Cortex-M4'
            self.CFLAGS += ' -e'
            self.CFLAGS += ' --fpu=VFPv4_sp'
            self.CFLAGS += ' --dlib_config "' + EXEC_PATH + '/arm/INC/c/DLib_Config_Normal.h"'
            self.CFLAGS += ' --silent'

            self.AFLAGS = DEVICE
            self.AFLAGS += ' -s+'
            self.AFLAGS += ' -w+'
            self.AFLAGS += ' -r'
            self.AFLAGS += ' --cpu Cortex-M4'
            self.AFLAGS += ' --fpu VFPv4_sp'
            self.AFLAGS += ' -S'

            if BUILD == 'debug':
                self.CFLAGS += ' --debug'
                self.CFLAGS += ' -On'
            else:
                self.CFLAGS += ' -Oh'

            self.LFLAGS = ' --config "board/linker_scripts/link.icf"'
            self.LFLAGS += ' --entry __iar_program_start'

            self.CXXFLAGS = self.CFLAGS

if __name__ == '__main__':
    arch = ARCHCortexM(Toochain = 'gcc')
    print(arch.CC)
