import biosteam as bst

class MyTEA(bst.TEA):
    def _FOC(self, FCI):
        return 0.2 * FCI  # 20% of FCI

tea = MyTEA(
    system=system,
    IRR=0.15,
    duration=(2025, 2035),
    depreciation='MACRS7',
    income_tax=0.30,
    operating_days=330,
    lang_factor= None,
    construction_schedule=(0.4, 0.6),
    startup_months=6,
    startup_FOCfrac=1.0,
    startup_VOCfrac=0.50,
    startup_salesfrac=0.5,
    WC_over_FCI=0.05,
    finance_interest=0.08,
    finance_years=10,
    finance_fraction=0.4,
)
annual_mass={}

mulch_film = film_bale.outs[0]
mulch_film.price = tea.solve_price(mulch_film)

print(mulch_film.price)
cf = tea.get_cashflow_table()
annual_mass['Mulch_film'] = (mulch_film.F_mass * 24 * tea.operating_days)

print(system.products)

print("\n===== TEA SUMMARY =====")

print(f"FCI                 : {tea.FCI:,.2f}")
print(f"TCI                 : {tea.TCI:,.2f}")
print(f"AOC (Total OPEX)    : {tea.AOC:,.2f} $/yr")
print(f"Utility Cost        : {tea.utility_cost:,.2f} $/yr")
print(f"Material Cost       : {tea.material_cost:,.2f} $/yr")
print(f"Sales               : {tea.sales:,.2f} $/yr")

cf = tea.get_cashflow_table()
print(cf)
npv = cf['Net present value (NPV) [MM$]'].sum()

print(f"NPV = {npv:.3f} MM$")

cf = tea.get_cashflow_table()

cum_npv = cf['Cumulative NPV [MM$]']

positive = cum_npv[cum_npv > 0]

if len(positive):
    payback = positive.index[0]
    print(f"Payback year: {payback}")
else:
    print("No payback achieved")
biofilm_IRR = tea.solve_IRR()
print(biofilm_IRR)