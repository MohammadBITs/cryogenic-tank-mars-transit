# =============================================================================
# Cryogenic Propellant Storage - Earth Mars Transit Thermal Analysis
# Author: Mohammad Shah
# Date: 04-04-2026
# Description: Parametric thermal model for LH2 storage over 240 day transit
# =============================================================================

import numpy as np
import matplotlib.pyplot as plt

# --- Global Plot Formatting ---
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.figsize'] = (8, 5)
plt.rcParams['lines.linewidth'] = 2

# --- Constants ---
sigma = 5.67e-8          # Stefan-Boltzmann constant (W/m2K4)
Lv = 446000              # Latent heat of vaporization LH2 (J/kg)
S0 = 1361                # Solar constant at 1 AU (W/m2)

# --- Tank Parameters ---
r_tank = 2               # Tank radius (m)
area = 4 * np.pi * r_tank**2  # Tank surface area (m2)
T_cold = 20.3            # LH2 boiling temperature (K)

# --- MLI Parameters ---
emissivity = 0.03        # Effective MLI emissivity

# --- Outer Surface Parameters ---
alpha_outer = 0.1        # Solar absorptivity of outer surface
emissivity_outer = 0.05  # Emissivity of outer surface

# --- Mission Parameters ---
duration_days = 240      # Mission duration (days)
r_earth = 1.0            # Earth orbital radius (AU)
r_mars = 1.524           # Mars orbital radius (AU)

# --- Cryocooler Parameters ---
COP = 0.05               # Coefficient of performance

# --- Optimization Parameters ---
specific_mass_MLI = 0.3        # MLI areal density (kg/m2 per layer)
specific_mass_power = 0.083    # Power system specific mass (kg/W)

# --- Functions ---

def heat_flux(N, T_hot):
    # Calculates radiative heat leak through MLI blanket (Watts)
    # Uses Stefan-Boltzmann law for N radiation shields between T_hot and T_cold
    # Formula derived from series resistance model for N shields with emissivity e on both sides
    # Q = sigma * A * (T_hot^4 - T_cold^4) / ((N+1) * (2/e - 1))
    return (sigma * emissivity * area * (T_hot**4 - T_cold**4)) / ((N + 1) * 2)

def boiloff_mass_daily(Q):
    # Converts heat flux Q (Watts) to propellant mass lost per day (kg/day)
    # Based on energy conservation at liquid-vapor interface: m_dot = Q / Lv
    return (Q / Lv) * 24 * 3600

def total_system_mass(N, Q_cool, T_hot):
    # Calculates total system mass (kg) for a given design point (N layers, Q_cool watts)
    # M_total = M_boiloff + M_MLI + M_power
    # M_boiloff: propellant lost over full mission duration
    # M_MLI: insulation mass from areal density * area * number of layers
    # M_power: power system mass to drive cryocooler = (Q_cool/COP) * specific_mass_power
    
    Q_passive = heat_flux(N, T_hot)        # Passive heat leak through MLI (W)
    Q_net = Q_passive - Q_cool             # Net heat load after active cooling (W)
    
    if Q_net > 0:
        # Cryocooler cannot fully compensate — residual boiloff occurs
        m_boiloff = (Q_net / Lv) * duration_days * 24 * 3600
    else:
        # Cryocooler fully compensates heat leak — zero boiloff achieved
        m_boiloff = 0
    
    m_MLI = N * area * specific_mass_MLI           # MLI blanket mass (kg)
    m_power = (Q_cool / COP) * specific_mass_power  # Power system mass (kg)
    
    return m_boiloff + m_MLI + m_power

# =============================================================================
# ANALYSIS 1 - Boiloff vs MLI Layers (Passive, T_hot = 300K fixed)
# =============================================================================

T_hot_fixed = 300  # Fixed external temperature for this analysis (K)

N_range = np.arange(1, 101)
boiloff_results = []

for N in N_range:
    Q = heat_flux(N, T_hot_fixed)
    mass_loss = (Q / Lv) * duration_days * 24 * 3600
    boiloff_results.append(mass_loss)

plt.figure()
plt.plot(N_range, boiloff_results)
plt.xlabel("Number of MLI Layers")
plt.ylabel("Mass Lost over 240 days (kg)")
plt.title("Boiloff Mass vs MLI Layers (T_hot = 300K)")
plt.grid(True)
plt.tight_layout()
plt.savefig('figure1.png', dpi=300, bbox_inches='tight')
plt.show()

# =============================================================================
# ANALYSIS 2 - Boiloff vs T_hot (Passive, N = 30 layers fixed)
# =============================================================================

N_fixed = 30  # Fixed MLI layer count for this analysis

T_hot_range = np.arange(200, 401)  # External temperature sweep (K)
boiloff_results_2 = []

for T_hot in T_hot_range:
    Q = heat_flux(N_fixed, T_hot)
    mass_loss = (Q / Lv) * duration_days * 24 * 3600
    boiloff_results_2.append(mass_loss)

plt.figure()
plt.plot(T_hot_range, boiloff_results_2)
plt.xlabel("External Surface Temperature (K)")
plt.ylabel("Mass Lost over 240 days (kg)")
plt.title("Boiloff Mass vs External Temperature (N = 30 layers)")
plt.grid(True)
plt.tight_layout()
plt.savefig('figure2.png', dpi=300, bbox_inches='tight')
plt.show()

# =============================================================================
# ANALYSIS 3 - Residual Boiloff vs Cooling Power (N=30, T_hot=300K)
# =============================================================================

N_fixed_3 = 30        # Fixed MLI layers for this analysis
T_hot_fixed_3 = 300   # Fixed external temperature for this analysis (K)

Q_passive_3 = heat_flux(N_fixed_3, T_hot_fixed_3)  # Passive heat leak (W)

Q_cool_range = np.linspace(0, Q_passive_3 * 2, 500)  # Sweep cooling power from 0 to 2x passive heat leak

boiloff_results_3 = []
power_results_3 = []

for Q_cool in Q_cool_range:
    Q_net = Q_passive_3 - Q_cool      # Net heat load after active cooling (W)
    P_input = Q_cool / COP            # Electrical power required to drive cryocooler (W)

    if Q_net > 0:
        # Residual boiloff occurs when cooling cannot fully offset heat leak
        residual_boiloff = (Q_net / Lv) * duration_days * 24 * 3600
    else:
        # Zero boiloff achieved
        residual_boiloff = 0

    boiloff_results_3.append(residual_boiloff)
    power_results_3.append(P_input)

# Figure 3 - Residual Boiloff vs Cooling Power
plt.figure()
plt.plot(Q_cool_range, boiloff_results_3)
plt.xlabel("Cooling Power (W)")
plt.ylabel("Residual Boiloff Mass over 240 days (kg)")
plt.title("Residual Boiloff vs Cooling Power (N=30, T_hot=300K)")
plt.grid(True)
plt.tight_layout()
plt.savefig('figure3.png', dpi=300, bbox_inches='tight')
plt.show()

# Figure 4 - Input Power vs Cooling Power
plt.figure()
plt.plot(Q_cool_range, power_results_3)
plt.xlabel("Cooling Power (W)")
plt.ylabel("Electrical Input Power (W)")
plt.title("Electrical Input Power vs Cooling Power (COP=0.05)")
plt.grid(True)
plt.tight_layout()
plt.savefig('figure4.png', dpi=300, bbox_inches='tight')
plt.show()

# =============================================================================
# ANALYSIS 4 - Passive vs Active Boiloff vs MLI Layers (T_hot=300K)
# =============================================================================

T_hot_fixed_4 = 300   # Fixed external temperature for this analysis (K)
N_ref = 30            # Reference layer count used to define Q_cool

# Q_cool is fixed at the passive heat leak at N=30 — the zero boiloff threshold at reference design
Q_cool_fixed_4 = heat_flux(N_ref, T_hot_fixed_4)  # Cooling power fixed at ZBO threshold (W)

N_range_4 = np.arange(1, 101)
passive_results_4 = []
active_results_4 = []

for N in N_range_4:
    Q_passive = heat_flux(N, T_hot_fixed_4)        # Passive heat leak at this layer count (W)
    Q_net = Q_passive - Q_cool_fixed_4             # Net heat load after active cooling (W)

    # Passive boiloff — no active cooling
    passive_boiloff = (Q_passive / Lv) * duration_days * 24 * 3600

    # Active boiloff — residual after cryocooler
    if Q_net > 0:
        active_boiloff = (Q_net / Lv) * duration_days * 24 * 3600
    else:
        active_boiloff = 0

    passive_results_4.append(passive_boiloff)
    active_results_4.append(active_boiloff)

# Figure 5 - Passive vs Active Boiloff vs MLI Layers
plt.figure()
plt.plot(N_range_4, passive_results_4, color='blue', label="Passive Only")
plt.plot(N_range_4, active_results_4, color='orange', label="Active Cooling")
plt.xlabel("Number of MLI Layers")
plt.ylabel("Mass Lost over 240 days (kg)")
plt.title("Passive vs Active Boiloff vs MLI Layers (T_hot=300K)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('figure5.png', dpi=300, bbox_inches='tight')
plt.show()

# =============================================================================
# ANALYSIS 5 - Total Mass Optimization (V-curve and 2D Contour)
# =============================================================================

T_hot_fixed_5 = 419   # Average T_hot from mission phase model (K)
Q_cool_fixed_5 = 110.0  # Fixed cooling power for V-curve (W)

# --- Figure 6: Total Mass vs MLI Layers (V-curve) ---
N_range_5 = np.arange(1, 101)
total_mass_list = []

for N in N_range_5:
    m_total = total_system_mass(N, Q_cool_fixed_5, T_hot_fixed_5)
    total_mass_list.append(m_total)

plt.figure()
plt.plot(N_range_5, total_mass_list)
plt.axvline(x=11, color='red', linestyle='--', label='Optimal N=11')
plt.xlabel("Number of MLI Layers")
plt.ylabel("Total System Mass (kg)")
plt.title("Total System Mass vs MLI Layers (Q_cool = 110W, T_hot = 419K)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('figure6.png', dpi=300, bbox_inches='tight')
plt.show()

# --- Optimal Point Finder ---
Q_cool_sweep = np.linspace(0, 700, 500)
N_sweep = np.arange(1, 101)

best_mass = float('inf')
best_N = 0
best_Q = 0

for N in N_sweep:
    for Q_cool in Q_cool_sweep:
        m = total_system_mass(N, Q_cool, T_hot_fixed_5)
        if m < best_mass:
            best_mass = m
            best_N = N
            best_Q = Q_cool

print(f"Optimal Design Point:")
print(f"  MLI Layers: {best_N}")
print(f"  Cooling Power: {best_Q:.2f} W")
print(f"  Minimum Total Mass: {best_mass:.2f} kg")

# --- Figure 7: 2D Contour - Total Mass Optimization Landscape ---
Q_range_5 = np.linspace(0, 700, 500)
N_grid, Q_grid = np.meshgrid(N_range_5, Q_range_5)

# Calculate heat flux across entire grid using corrected formula
boil_off_grid = (sigma * emissivity * area * (T_hot_fixed_5**4 - T_cold**4)) / ((N_grid + 1) * 2)
Q_net_grid = boil_off_grid - Q_grid
m_boiloff_grid = np.where(Q_net_grid > 0, (Q_net_grid / Lv) * duration_days * 24 * 3600, 0)
m_MLI_grid = N_grid * area * specific_mass_MLI
m_power_grid = (Q_grid / COP) * specific_mass_power
M_total_grid = m_boiloff_grid + m_MLI_grid + m_power_grid

plt.figure()
contour = plt.contourf(N_range_5, Q_range_5, M_total_grid, levels=50, cmap='viridis')
plt.colorbar(contour, label='Total System Mass (kg)')
plt.xlabel('Number of MLI Layers')
plt.ylabel('Cooling Power (W)')
plt.title('Total System Mass Optimization Landscape (T_hot = 419K)')
plt.plot(best_N, best_Q, 'r*', markersize=15, label=f'Optimal: N={best_N}, Q={best_Q:.1f}W')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('figure7.png', dpi=300, bbox_inches='tight')
plt.show()

# =============================================================================
# ANALYSIS 6 - Mission Phase Thermal Model (Time-Varying T_hot)
# =============================================================================

N_mli_6 = 11          # Optimal MLI layer count from Analysis 5
Q_cool_6 = 110.83     # Optimal cooling power from Analysis 5 (W)

r_initial = 1.0       # Earth orbital radius (AU)
r_final = 1.524       # Mars orbital radius (AU)

cum_boiloff_passive = 0.0   # Cumulative passive boiloff mass (kg)
cum_boiloff_active = 0.0    # Cumulative active boiloff mass (kg)

mission_data = []     # Stores daily data for plotting

for t in range(0, 241):
    # Heliocentric distance — linear interpolation from Earth to Mars (AU)
    r = (r_final - r_initial) * t / 240 + r_initial

    # Solar flux at current distance (W/m2)
    S_r = S0 / (r**2)

    # Outer surface equilibrium temperature from radiative balance (K)
    T_hot_t = ((alpha_outer * S_r) / (emissivity_outer * sigma))**0.25

    # Passive heat leak through MLI at current T_hot (W)
    Q_passive_t = heat_flux(N_mli_6, T_hot_t)

    # Daily passive boiloff mass (kg/day)
    daily_passive = (Q_passive_t / Lv) * 24 * 3600

    # Net heat load after active cooling (W)
    Q_net_t = Q_passive_t - Q_cool_6

    # Daily active boiloff mass (kg/day)
    if Q_net_t > 0:
        daily_active = (Q_net_t / Lv) * 24 * 3600
    else:
        daily_active = 0

    # Accumulate cumulative mass loss
    cum_boiloff_passive += daily_passive
    cum_boiloff_active += daily_active

    mission_data.append((t, r, S_r, T_hot_t, cum_boiloff_passive, cum_boiloff_active))

# Print final results
print(f"Total passive boiloff over 240 days: {cum_boiloff_passive:.2f} kg")
print(f"Total active boiloff over 240 days: {cum_boiloff_active:.2f} kg")
print(f"Propellant saved by active cooling: {cum_boiloff_passive - cum_boiloff_active:.2f} kg")
avg_T_hot = np.mean([d[3] for d in mission_data])
print(f"Average T_hot over mission: {avg_T_hot:.2f} K")

# Figure 8 - T_hot vs Mission Day
days = [d[0] for d in mission_data]
T_hot_list = [d[3] for d in mission_data]

plt.figure()
plt.plot(days, T_hot_list, color='orange')
plt.xlabel("Mission Day")
plt.ylabel("External Surface Temperature (K)")
plt.title("External Tank Temperature vs Mission Day")
plt.grid(True)
plt.tight_layout()
plt.savefig('figure8.png', dpi=300, bbox_inches='tight')
plt.show()

# --- Zero Boiloff Day Finder ---
# Identifies the first mission day where active cooling fully eliminates boiloff
zbo_day = None
for d in mission_data:
    t = d[0]
    T_hot_t = d[3]
    Q_passive_t = heat_flux(N_mli_6, T_hot_t)
    if Q_passive_t <= Q_cool_6:
        zbo_day = t
        break

if zbo_day is not None:
    print(f"Zero boiloff first achieved on day: {zbo_day}")
else:
    print("Zero boiloff not achieved during mission")


# Figure 9 - Cumulative Boiloff Passive vs Active
passive_list = [d[4] for d in mission_data]
active_list = [d[5] for d in mission_data]

plt.figure()
plt.plot(days, passive_list, color='blue', label="Passive Only")
plt.plot(days, active_list, color='orange', label="Active Cooling")
plt.axvline(x=111, color='gray', linestyle='--', alpha=0.7, label='Near-ZBO threshold (~day 150)')
plt.xlabel("Mission Day")
plt.ylabel("Cumulative Mass Loss (kg)")
plt.title("Cumulative Boiloff Mass vs Mission Day (N=11, Q_cool=110W)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('figure9.png', dpi=300, bbox_inches='tight')
plt.show()


print("All figures saved successfully.")