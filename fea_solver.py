"""
텐세그리티 구조 FEA 솔버
- 트러스/빔 요소 기반
- 응력, 변형률, 변위 계산
- 번개 패널 중앙에 스트링 장력으로 하중 전달
- L자 브라켓: 상단 삼각형 한 꼭지점(Top2)과 하단 삼각형 같은 위치(Bottom2)에 연결
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings('ignore')

from config import *

class TensegrityFEA:
    """텐세그리티 구조 유한요소해석"""
    
    def __init__(self):
        self.nodes = {}          # 노드 좌표
        self.elements = {}       # 요소 정보
        self.materials = {}      # 재료 특성
        self.boundary_conditions = {}  # 경계조건
        self.displacements = None
        self.stresses = None
        self.strains = None
        self.node_map = {}
        
    def create_geometry(self):
        """기하학적 형상 생성
        
        구조:
        - 상단 삼각형 (3개 꼭지점, 고정)
        - 하단 삼각형 (3개 꼭지점, 고정)
        - L자 브라켓 상단 (Top2 꼭지점에 연결)
        - L자 브라켓 하단 (Bottom2 꼭지점에 연결)
        - 번개 패널 중심 (브라켓 스트링으로 연결, 떠있음)
        """
        print("기하학적 형상 생성 중...")
        
        # 정삼각형 좌표 계산 (무게중심 기준)
        h = TRIANGLE_SIDE * np.sqrt(3) / 2
        
        node_id = 1
        
        # ===== 상단 삼각형 (위에서 봤을 때 반시계방향) =====
        top_center_z = HEIGHT_BETWEEN / 2
        
        # Top1
        self.nodes[node_id] = np.array([0, TRIANGLE_SIDE/(2*np.sqrt(3)), top_center_z])
        top1 = node_id
        node_id += 1
        
        # Top2 (L자 브라켓이 연결되는 위치)
        self.nodes[node_id] = np.array([-TRIANGLE_SIDE/2, -TRIANGLE_SIDE/(2*np.sqrt(3)), top_center_z])
        top2 = node_id
        node_id += 1
        
        # Top3
        self.nodes[node_id] = np.array([TRIANGLE_SIDE/2, -TRIANGLE_SIDE/(2*np.sqrt(3)), top_center_z])
        top3 = node_id
        node_id += 1
        
        # ===== 하단 삼각형 (위에서 봤을 때 반시계방향) =====
        bottom_center_z = -HEIGHT_BETWEEN / 2
        
        # Bottom1
        self.nodes[node_id] = np.array([0, TRIANGLE_SIDE/(2*np.sqrt(3)), bottom_center_z])
        bottom1 = node_id
        node_id += 1
        
        # Bottom2 (L자 브라켓이 연결되는 위치)
        self.nodes[node_id] = np.array([-TRIANGLE_SIDE/2, -TRIANGLE_SIDE/(2*np.sqrt(3)), bottom_center_z])
        bottom2 = node_id
        node_id += 1
        
        # Bottom3
        self.nodes[node_id] = np.array([TRIANGLE_SIDE/2, -TRIANGLE_SIDE/(2*np.sqrt(3)), bottom_center_z])
        bottom3 = node_id
        node_id += 1
        
        # ===== L자 브라켓 상단 (Top2에서 아래로) =====
        bracket_top_pos = self.nodes[top2].copy()
        bracket_top_pos[2] -= BRACKET_OFFSET  # Z 방향으로 약간 아래
        self.nodes[node_id] = bracket_top_pos
        bracket_top = node_id
        node_id += 1
        
        # ===== L자 브라켓 하단 (Bottom2에서 위로) =====
        bracket_bottom_pos = self.nodes[bottom2].copy()
        bracket_bottom_pos[2] += BRACKET_OFFSET  # Z 방향으로 약간 위
        self.nodes[node_id] = bracket_bottom_pos
        lightning_center = node_id
        node_id += 1
        
        # ===== 번개 패널 중심 (중간에 떠있음) =====
        # 상단 브라켓과 하단 브라켓 위치의 중간
        self.nodes[node_id] = np.array([
            self.nodes[bracket_top][0],
            self.nodes[bracket_top][1],
            0  # 중앙 높이
        ])
        lightning_center = node_id
        node_id += 1
        
        self.node_map = {
            'top1': top1, 'top2': top2, 'top3': top3,
            'bottom1': bottom1, 'bottom2': bottom2, 'bottom3': bottom3,
            'bracket_top': bracket_top, 'bracket_bottom': bracket_bottom_pos,
            'lightning_center': lightning_center
        }
        
        print(f"  총 {len(self.nodes)}개 노드 생성")
        for i, pos in self.nodes.items():
            print(f"    Node {i}: ({pos[0]:.4f}, {pos[1]:.4f}, {pos[2]:.4f})")
        
        return self.node_map
    
    def create_elements(self, node_map):
        """요소 생성 (빔/트러스)"""
        print("\n요소 생성 중...")
        
        elem_id = 1
        
        # ===== 상단 삼각형 프레임 (목재) =====
        frame_elements = [
            (node_map['top1'], node_map['top2'], 'wood'),
            (node_map['top2'], node_map['top3'], 'wood'),
            (node_map['top3'], node_map['top1'], 'wood'),
        ]
        
        # ===== 하단 삼각형 프레임 (목재) =====
        frame_elements.extend([
            (node_map['bottom1'], node_map['bottom2'], 'wood'),
            (node_map['bottom2'], node_map['bottom3'], 'wood'),
            (node_map['bottom3'], node_map['bottom1'], 'wood'),
        ])
        
        # ===== 수직 스트링 (상단/하단 삼각형 연결) =====
        string_elements = [
            (node_map['top1'], node_map['bottom1'], 'string'),
            (node_map['top2'], node_map['bottom2'], 'string'),
            (node_map['top3'], node_map['bottom3'], 'string'),
        ]
        
        # ===== L자 브라켓 (강철) =====
        # 상단 브라켓: Top2 - bracket_top
        bracket_elements = [
            (node_map['top2'], node_map['bracket_top'], 'bracket'),
            (node_map['bottom2'], node_map['bracket_bottom'], 'bracket'),
        ]
        
        # ===== 스트링 (번개 패널 연결) =====
        # 상단 브라켓에서 번개 패널로
        string_elements.extend([
            (node_map['bracket_top'], node_map['lightning_center'], 'string'),
            (node_map['bracket_bottom'], node_map['lightning_center'], 'string'),
        ])
        
        # 모든 요소 추가
        for n1, n2, mat in frame_elements + bracket_elements + string_elements:
            self.elements[elem_id] = {
                'nodes': (n1, n2),
                'material': mat,
                'type': 'truss'
            }
            elem_id += 1
        
        print(f"  총 {len(self.elements)}개 요소 생성")
        print(f"    - 목재 프레임: 6개")
        print(f"    - 수직 스트링: 3개")
        print(f"    - L자 브라켓: 2개")
        print(f"    - 번개패널 스트링: 2개")
    
    def set_materials(self):
        """재료 특성 설정"""
        self.materials['wood'] = {
            'E': WOOD_YOUNGS_MODULUS,
            'nu': WOOD_POISSON,
            'area': WOOD_SECTION_AREA,
            'density': WOOD_DENSITY,
            'name': '목재'
        }
        
        self.materials['string'] = {
            'E': STRING_YOUNGS_MODULUS,
            'nu': STRING_POISSON,
            'area': STRING_SECTION_AREA,
            'density': 1000,
            'name': '나일론 스트링'
        }
        
        self.materials['bracket'] = {
            'E': STEEL_YOUNGS_MODULUS,
            'nu': STEEL_POISSON,
            'area': WOOD_SECTION_AREA * 0.5,  # 강철 브라켓는 더 얇음
            'density': STEEL_DENSITY,
            'name': '강철 브라켓'
        }
        
        print(f"\n재료 특성 설정:")
        for mat_name, props in self.materials.items():
            print(f"  {props['name']}: E={props['E']/1e9:.1f}GPa, A={props['area']*1e6:.3f}mm²")
    
    def set_boundary_conditions(self, node_map):
        """경계조건 설정"""
        print("\n경계조건 설정 중...")
        
        # 상단 삼각형 모두 고정
        self.boundary_conditions[node_map['top1']] = np.array([0, 0, 0])
        self.boundary_conditions[node_map['top2']] = np.array([0, 0, 0])
        self.boundary_conditions[node_map['top3']] = np.array([0, 0, 0])
        
        # 하단 삼각형 모두 고정
        self.boundary_conditions[node_map['bottom1']] = np.array([0, 0, 0])
        self.boundary_conditions[node_map['bottom2']] = np.array([0, 0, 0])
        self.boundary_conditions[node_map['bottom3']] = np.array([0, 0, 0])
        
        print(f"  {len(self.boundary_conditions)}개 경계조건 설정 (상단/하단 삼각형 고정)")
    
    def solve_static(self, load_scale=1.0):
        """정적해석 풀이 (간단한 버전)"""
        print(f"\n정적해석 풀이 중 (하중 계수: {load_scale})...")
        
        # 변위 벡터 초기화
        num_nodes = len(self.nodes)
        U = np.zeros(3 * num_nodes)
        
        # 간단한 근사: 번개 패널의 변위만 계산
        # 스트링 장력에 의한 변위
        lightning_node = self.node_map['lightning_center']
        lightning_dof = 3 * (lightning_node - 1)
        
        # 스트링 길이와 강성 계산
        bracket_top_pos = self.nodes[self.node_map['bracket_top']]
        lightning_pos = self.nodes[lightning_node]
        
        string_length = np.linalg.norm(lightning_pos - bracket_top_pos)
        string_stiffness = self.materials['string']['E'] * self.materials['string']['area'] / string_length
        
        # 번개 패널 변위 (Z 방향 하향)
        # 두 개의 스트링이 지탱하므로
        total_stiffness = 2 * string_stiffness
        displacement_z = -PHONE_WEIGHT * load_scale / total_stiffness
        
        U[lightning_dof + 2] = displacement_z  # Z 방향
        
        # 응력 계산
        self.calculate_stress(U)
        
        self.displacements = U
        print(f"  번개 패널 변위: {abs(displacement_z):.6e} m ({abs(displacement_z)*1000:.4f} mm)")
        print(f"  번개 패널 위치: z = {lightning_pos[2] + displacement_z:.6f} m")
    
    def calculate_stress(self, U):
        """응력 계산"""
        stresses = {}
        
        for elem_id, elem in self.elements.items():
            n1, n2 = elem['nodes']
            mat = self.materials[elem['material']]
            
            # 노드 좌표
            pos1 = self.nodes[n1]
            pos2 = self.nodes[n2]
            
            # 초기 길이
            L0 = np.linalg.norm(pos2 - pos1)
            
            # 노드 변위
            u1 = U[3*(n1-1):3*n1]
            u2 = U[3*(n2-1):3*n2]
            
            # 변위 후 위치
            new_pos1 = pos1 + u1
            new_pos2 = pos2 + u2
            
            # 새로운 길이
            L = np.linalg.norm(new_pos2 - new_pos1)
            
            # 변형률
            strain = (L - L0) / L0
            
            # 응력
            stress = mat['E'] * strain
            
            stresses[elem_id] = {
                'stress': stress,
                'strain': strain,
                'element': elem_id,
                'material': elem['material']
            }
        
        self.stresses = stresses
    
    def visualize_structure(self):
        """구조 시각화"""
        print("\n구조 시각화 중...")
        
        fig = plt.figure(figsize=(16, 12), dpi=100)
        
        # 원본 구조 (3D)
        ax1 = fig.add_subplot(2, 2, 1, projection='3d')
        self._plot_structure_3d(ax1, self.nodes, show_deformed=False)
        ax1.set_title('원본 구조', fontsize=12, fontweight='bold')
        
        # 변형된 구조 (3D)
        if self.displacements is not None:
            ax2 = fig.add_subplot(2, 2, 2, projection='3d')
            deformed_nodes = self._get_deformed_nodes(DEFORMATION_SCALE)
            self._plot_structure_3d(ax2, deformed_nodes, show_deformed=True)
            ax2.set_title(f'변형된 구조 (확대 {DEFORMATION_SCALE}배)', fontsize=12, fontweight='bold')
        
        # 응력 분포
        if self.stresses:
            ax3 = fig.add_subplot(2, 2, 3)
            self._plot_stress_distribution(ax3)
        
        # 변형률 분포
        if self.stresses:
            ax4 = fig.add_subplot(2, 2, 4)
            self._plot_strain_distribution(ax4)
        
        plt.tight_layout()
        return fig
    
    def _plot_structure_3d(self, ax, nodes, show_deformed=False):
        """3D 구조 그리기"""
        # 노드 좌표
        node_ids = sorted(nodes.keys())
        node_coords = np.array([nodes[i] for i in node_ids])
        
        # 노드 플롯
        ax.scatter(node_coords[:, 0], node_coords[:, 1], node_coords[:, 2],
                  c='red', s=100, marker='o', zorder=5, label='노드')
        
        # 요소 플롯
        for elem_id, elem in self.elements.items():
            n1, n2 = elem['nodes']
            pos1 = nodes[n1]
            pos2 = nodes[n2]
            
            x = [pos1[0], pos2[0]]
            y = [pos1[1], pos2[1]]
            z = [pos1[2], pos2[2]]
            
            if elem['material'] == 'wood':
                ax.plot(x, y, z, 'b-', linewidth=3, label='목재 프레임' if elem_id == 1 else '')
            elif elem['material'] == 'bracket':
                ax.plot(x, y, z, 'r-', linewidth=2, label='L자 브라켓' if elem_id == 7 else '')
            elif elem['material'] == 'string':
                ax.plot(x, y, z, 'g--', linewidth=1.5, label='스트링' if elem_id == 9 else '')
        
        # 축 설정
        all_coords = node_coords
        max_range = np.array([all_coords[:, 0].max()-all_coords[:, 0].min(),
                             all_coords[:, 1].max()-all_coords[:, 1].min(),
                             all_coords[:, 2].max()-all_coords[:, 2].min()]).max() / 2.0
        mid_x = (all_coords[:, 0].max() + all_coords[:, 0].min()) * 0.5
        mid_y = (all_coords[:, 1].max() + all_coords[:, 1].min()) * 0.5
        mid_z = (all_coords[:, 2].max() + all_coords[:, 2].min()) * 0.5
        
        ax.set_xlim(mid_x - max_range*1.2, mid_x + max_range*1.2)
        ax.set_ylim(mid_y - max_range*1.2, mid_y + max_range*1.2)
        ax.set_zlim(mid_z - max_range*1.2, mid_z + max_range*1.2)
        
        ax.set_xlabel('X (m)', fontsize=10)
        ax.set_ylabel('Y (m)', fontsize=10)
        ax.set_zlabel('Z (m)', fontsize=10)
        ax.legend(loc='upper right', fontsize=8)
    
    def _get_deformed_nodes(self, scale):
        """변형된 노드 좌표"""
        deformed = {}
        for node_id in self.nodes:
            dof_start = 3 * (node_id - 1)
            deformed[node_id] = self.nodes[node_id] + scale * self.displacements[dof_start:dof_start+3]
        return deformed
    
    def _plot_stress_distribution(self, ax):
        """응력 분포 그래프"""
        if not self.stresses:
            return
        
        elem_ids = sorted(self.stresses.keys())
        stresses = [abs(self.stresses[e]['stress']) for e in elem_ids]
        materials = [self.stresses[e]['material'] for e in elem_ids]
        
        # 재료별 색상
        color_map = {'wood': 'blue', 'string': 'green', 'bracket': 'red'}
        colors = [color_map[mat] for mat in materials]
        
        bars = ax.bar(range(len(stresses)), stresses, color=colors, alpha=0.7)
        
        ax.set_xlabel('요소 ID', fontsize=11)
        ax.set_ylabel('응력 (Pa)', fontsize=11)
        ax.set_title('응력 분포', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_yscale('log')
        
        # 범례
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='blue', alpha=0.7, label='목재'),
            Patch(facecolor='green', alpha=0.7, label='스트링'),
            Patch(facecolor='red', alpha=0.7, label='브라켓')
        ]
        ax.legend(handles=legend_elements, fontsize=9)
    
    def _plot_strain_distribution(self, ax):
        """변형률 분포 그래프"""
        if not self.stresses:
            return
        
        elem_ids = sorted(self.stresses.keys())
        strains = [abs(self.stresses[e]['strain']) for e in elem_ids]
        materials = [self.stresses[e]['material'] for e in elem_ids]
        
        # 재료별 색상
        color_map = {'wood': 'blue', 'string': 'green', 'bracket': 'red'}
        colors = [color_map[mat] for mat in materials]
        
        bars = ax.bar(range(len(strains)), strains, color=colors, alpha=0.7)
        
        ax.set_xlabel('요소 ID', fontsize=11)
        ax.set_ylabel('변형률', fontsize=11)
        ax.set_title('변형률 분포', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        # 범례
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='blue', alpha=0.7, label='목재'),
            Patch(facecolor='green', alpha=0.7, label='스트링'),
            Patch(facecolor='red', alpha=0.7, label='브라켓')
        ]
        ax.legend(handles=legend_elements, fontsize=9)
    
    def print_results(self):
        """결과 출력"""
        print("\n" + "="*60)
        print("해석 결과 요약")
        print("="*60)
        
        if self.stresses:
            print("\n[응력 분포]")
            for elem_id in sorted(self.stresses.keys()):
                stress = self.stresses[elem_id]['stress']
                strain = self.stresses[elem_id]['strain']
                mat = self.stresses[elem_id]['material']
                print(f"  요소 {elem_id:2d} ({mat:8s}): 응력={stress:12.2e} Pa, 변형률={strain:12.6e}")
        
        if self.displacements is not None:
            print("\n[최대 변위]")
            max_disp = np.max(np.abs(self.displacements))
            print(f"  최대 변위: {max_disp:.6e} m ({max_disp*1000:.4f} mm)")
            
            lightning_node = self.node_map['lightning_center']
            lightning_dof = 3 * (lightning_node - 1)
            print(f"  번개 패널 Z 방향 변위: {self.displacements[lightning_dof+2]:.6e} m")
    
    def run_analysis(self):
        """전체 해석 실행"""
        print("\n" + "="*60)
        print("텐세그리티 구조 FEA 시뮬레이션")
        print("="*60)
        
        # 기하학적 형상 생성
        self.create_geometry()
        
        # 요소 생성
        self.create_elements(self.node_map)
        
        # 재료 특성 설정
        self.set_materials()
        
        # 경계조건 설정
        self.set_boundary_conditions(self.node_map)
        
        # 정적해석 풀이
        self.solve_static(load_scale=1.0)
        
        # 결과 출력
        self.print_results()
        
        # 시각화
        fig = self.visualize_structure()
        
        return fig


# ========== 메인 실행 ==========
if __name__ == "__main__":
    # FEA 솔버 생성 및 실행
    fea = TensegrityFEA()
    fig = fea.run_analysis()
    
    # 결과 저장
    plt.savefig('tensegrity_analysis_results.png', dpi=150, bbox_inches='tight')
    print("\n결과 저장: tensegrity_analysis_results.png")
    
    plt.show()
