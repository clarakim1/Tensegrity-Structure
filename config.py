# ==========================================
# 텐세그리티 구조 - 설정 파일
# ==========================================

# 기하학적 치수 (미터)
TRIANGLE_SIDE = 0.12         # 삼각형 한 변 길이 (m) - 120mm
HEIGHT_BETWEEN = 0.08        # 상단/하단 삼각형 간 높이 (m)
LIGHTNING_WIDTH = 0.05       # 번개 패널 폭 (m)
LIGHTNING_HEIGHT = 0.03      # 번개 패널 높이 (m)

# 재료 특성
# 목재 (소나무)
WOOD_YOUNGS_MODULUS = 11e9   # Pa (11 GPa)
WOOD_POISSON = 0.3
WOOD_DENSITY = 500           # kg/m³
WOOD_SECTION_WIDTH = 0.01    # m (10 mm)
WOOD_SECTION_HEIGHT = 0.01   # m (10 mm)
WOOD_SECTION_AREA = WOOD_SECTION_WIDTH * WOOD_SECTION_HEIGHT

# 스트링 (나일론 로프)
STRING_YOUNGS_MODULUS = 5e9  # Pa (5 GPa, 나일론)
STRING_POISSON = 0.3
STRING_DIAMETER = 0.00175    # m (1.75 mm)
STRING_SECTION_AREA = 3.14159 * (STRING_DIAMETER/2)**2

# 강철 브라켓
STEEL_YOUNGS_MODULUS = 200e9 # Pa (200 GPa)
STEEL_POISSON = 0.3
STEEL_DENSITY = 7850         # kg/m³
BRACKET_LENGTH = 0.02        # L자 브라켓 길이 (m) - 20mm
BRACKET_OFFSET = 0.01        # 브라켓이 꼭지점에서 떨어진 거리

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

# ===== 구조 설명 =====
# 상단 삼각형: 3개 꼭지점 (고정)
# 하단 삼각형: 3개 꼭지점 (고정)
# L자 브라켓 위: 상단 삼각형 한 꼭지점(Top2)에 연결
# L자 브라켓 아래: 하단 삼각형 같은 위치(Bottom2)에 연결
# 번개 패널: 중앙에 떠있음 (상단 브라켓 스트링 + 하단 브라켓 스트링으로 지탱)
# 스트링 장력: 번개 패널 중심에 휴대폰 무게가 걸려 장력 생성
