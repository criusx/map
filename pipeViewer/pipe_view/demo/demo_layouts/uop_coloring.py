import re

DEFAULT_COLOR = (255, 255, 255)
LS_COLOR = (230, 230, 0)
FP_COLOR = (90, 230, 90)
FP_SHUFFLE_COLOR = (75, 190, 140)
INT_COLOR = (92, 166, 235)
BRANCH_COLOR = (0, 230, 230)
OTHER_COLOR = (255, 0, 0)
A64_COLOR = (200, 117, 222)
A32_COLOR = (255, 150, 60)
T32_COLOR = (255, 160, 160)

def BuildTuple(color, anno):
    return color + (anno,)

def CheckInvalidAnno(anno):
    empty_re = re.compile('<.*>')
    if anno == '' or empty_re.match(anno) is not None:
        return True

    return False

def FetchColoring(anno):
    vaddr_re = re.compile('vas=([0-9a-fx]+)')
    is_re = re.compile('is=(a64|a32|t32|---)\s')

    vaddr_match = vaddr_re.search(anno)
    is_match = is_re.search(anno)

    if CheckInvalidAnno(anno) or vaddr_match is None or is_match is None:
        return BuildTuple(DEFAULT_COLOR, '')

    vaddr = int(vaddr_match.group(1), 16)
    istate = is_match.group(1)
    if istate == 'a64':
        color = A64_COLOR
    elif istate == 'a32':
        color = A32_COLOR
    elif istate == 't32':
        color = T32_COLOR
    else:
        color = DEFAULT_COLOR

    return BuildTuple(color, hex(vaddr))

def LSColoring(anno):
    vaddr_re = re.compile('v=([0-9a-f]+)')

    if CheckInvalidAnno(anno) or vaddr_re.search(anno) is None:
        return BuildTuple(DEFAULT_COLOR, '')

    vaddr = int(vaddr_re.search(anno).group(1), 16)
    return BuildTuple(LS_COLOR, hex(vaddr))

def UopColoring(anno):
        #INT_ARITHMETIC,
        #INT_LOGICAL,
        #INT_SAT,
        #INT_CLS_CLZ,
        #INT_SHIFT,
        #INT_FLAGS,
        #INT_CC_CHECK,
        #INT_INDIR_BRANCH,
        #INT_DIR_BRANCH,
        #INT_SPR,
        #INT_DIV,
        #INT_MUL,
        #INT_LOAD,
        #INT_STORE,
        #FP_FADD,
        #FP_FMUL,
        #FP_CONVERT,
        #FP_FMAC,
        #FP_SIMD_MOVE,
        #FP_SCALAR_MOVE,
        #FP_CMP,
        #FP_CRYPTO,
        #FP_DIV_SQRT,
        #FP_LOAD,
        #FP_STORE,
        #FP_FLAGS_MOVE,
        #UNKNOWN,
        #ROB,
        #FP_MISC,
        #FP_SIMD_ALU,
        #FP_SIMD_SHUF,
        #FP_SIMD_MISC,
        #FP_SIMD_MUL,
        #INT_DIR_BRANCH_REGRD,
        #FP_SIMD_SHIFT,
        #FP_SIMD_SHUFFLE,
        #FP_SIMD_IADD,
        #INT_INS,
        #FP_STORE_ONLY,
    def GetUopAnnotation(anno):
        anno_items = anno.split()
        return anno_items[1]

    def GetUopAnnotationAndColor(color, anno):
        return BuildTuple(color, GetUopAnnotation(anno))

    if CheckInvalidAnno(anno):
        return BuildTuple(DEFAULT_COLOR, '')
    else:
        if 'LOAD' in anno or 'STORE' in anno:
            return GetUopAnnotationAndColor(LS_COLOR, anno)
        elif 'BRANCH' in anno:
            return GetUopAnnotationAndColor(BRANCH_COLOR, anno)
        elif 'FP_SIMD_SHUFFLE' in anno and 'fmla' in anno:
            return GetUopAnnotationAndColor(FP_SHUFFLE_COLOR, anno)
        elif 'FP' in anno:
            return GetUopAnnotationAndColor(FP_COLOR, anno)
        elif 'INT' in anno:
            return GetUopAnnotationAndColor(INT_COLOR, anno)
        else:
            return GetUopAnnotationAndColor(OTHER_COLOR, anno)
