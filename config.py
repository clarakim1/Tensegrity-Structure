# ==========================================
# 텐세그리티 구조 - 설정 파일
# ==========================================

# 기하학적 치수 (미터)
TRIANGLE_SIDE = 1.0          # 삼각형 한 변 길이 (m)
HEIGHT_BETWEEN = 0.8         # 상단/하단 삼각형 간 높이 (m)
LIGHTNING_WIDTH = 0.5        # 번개 패널 폭 (m)
LIGHTNING_HEIGHT = 0.3       # 번개 패널 높이 (m)

# 재료 특성
# 목재 (소나무)
WOOD_YOUNGS_MODULUS = 11e9   # Pa (11 GPa)
WOOD_POISSON = 0.3
WOOD_DENSITY = 500           # kg/m³
WOOD_SECTION_WIDTH = 0.05    # m (50 mm)
WOOD_SECTION_HEIGHT = 0.05   # m (50 mm)
WOOD_SECTION_AREA = WOOD_SECTION_WIDTH * WOOD_SECTION_HEIGHT

# 스트링 (나일론 로프)
STRING_YOUNGS_MODULUS = 5e9  # Pa (5 GPa, 나일론)
STRING_POISSON = 0.3
STRING_DIAMETER = 0.005      # m (5 mm)
STRING_SECTION_AREA = 3.14159 * (STRING_DIAMETER/2)**2

# 강철 브라켓
STEEL_YOUNGS_MODULUS = 200e9 # Pa (200 GPa)
STEEL_POISSON = 0.3
STEEL_DENSITY = 7850         # kg/m³

# 하중 조건
PHONE_MASS = 0.2             # kg (200g)
GRAVITY = 9.81               # m/s²
PHONE_WEIGHT = PHONE_MASS * GRAVITY  # N

# 시뮬레이션 설정
NUM_LOAD_STEPS = 5           # 하중 단계 수
SOLVER_TOLERANCE = 1e-6      # 수렴 허용도
MAX_ITERATIONS = 100         # 최대 반복 횟수

# 시각화 설정
PLOT_DPI = 100
PLOT_FIGSIZE = (15, 12)
STRESS_COLORMAP = 'RdYlBu_r'
SHOW_DEFORMATION = True
DEFORMATION_SCALE = 100      # 변위 확대 배수
