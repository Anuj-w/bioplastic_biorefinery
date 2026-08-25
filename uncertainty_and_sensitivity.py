import biosteam as bst
import numpy as np
import pandas as pd
from chaospy import distributions as shape
from warnings import filterwarnings;

model = bst.Model(system)
@model.indicator(units= 'USD/kg')
def MSP():
    return tea.solve_price(mulch_film)
@model.indicator(units ='10^6*USD')
def TCI():
    return tea.TCI/1e6

@model.indicator(units = '%')
def IRR():
    return tea.solve_IRR()*100
@model.indicator(units = '$')
def NPV():
    return tea.NPV
@model.indicator(units = '$/yr')
def AOC():
    return tea.AOC
@model.indicator(units = '$')
def FCI():
    return tea.FCI

baseline_pla = polymer.F_mass
baseline_peg = plasticizer.F_mass
baseline_lignin = filler.F_mass

ratio_pla = baseline_pla/baseline_lignin
ratio_peg = baseline_peg/baseline_lignin

baseline_total_feed = baseline_lignin * (
    1 + ratio_pla + ratio_peg
)

@model.parameter(
    element='Feed',
    units='kg/hr',
    bounds=(
        0.8 * baseline_total_feed,
        1.2 * baseline_total_feed
    ),
    baseline=baseline_total_feed,
    distribution='triangular',
    coupled=True,
)
def set_feedrate(total_feed):

    filler.F_mass = total_feed / (
        1 + ratio_pla + ratio_peg
    )

    polymer.F_mass = filler.F_mass * ratio_pla

    plasticizer.F_mass = filler.F_mass * ratio_peg

pla = polymer

@model.parameter(
    element='PLA',
    units='$/kg',
    bounds=(2.25,2.75),
    baseline=pla.price,
    distribution='Triangular',
)
def set_pla_price(price):
    pla.price = price

lig = filler

@model.parameter(
    element='Lignin',
    units='$/kg',
    bounds=(0.85, 1.35),
    baseline=lig.price,
    distribution='Triangular',
)
def set_lignin_price(price):
    lig.price = price

peg = plasticizer

@model.parameter(
    element = 'PEG400',
    units = '$/kg',
    bounds = (1.75, 2.25),
    baseline = peg.price,
    distribution = 'Triangular'
)
def set_peg_price(price):
    peg.price = price

film = lignin_pla_film

@model.parameter(
    element='Film extrusion',
    units='fraction',
    bounds=(0.94,0.99),
    baseline=film.film_yield,
    distribution='triangular',
    coupled=True,
)
def set_film_yield(y):
    film.film_yield = y
np.random.seed(1234)
samples = model.sample(N =10000, rule = 'L')
model.load_samples(samples, sort = True)
model.evaluate()
results = model.table.copy()
results
#results.to_excel('biofilm_monte_carlo_2_kg_flow_rate.xlsx')

# montecarlo plots and uncertainty analysis

format_units = tmo.units_of_measure.format_units
ylabel = f"MSP [{format_units('USD/kg')}]"
xlabel = f"TCI [{format_units('10^6 USD')}]"
def plot_uncertainty(table): # This function will be useful later
    fig, ax, axes = bst.plots.plot_kde(
        y=table[MSP.index],
        x=table[TCI.index],
        ylabel=ylabel,
        xlabel=xlabel,
        aspect_ratio=1.1,
    )
plot_uncertainty(model.table)

msp = model.table['-', 'MSP [USD/kg]']

print("Mean MSP:", msp.mean())
print("Median MSP:", msp.median())
print("Minimum MSP:", msp.min())
print("Maximum MSP:", msp.max())
print("Standard deviation:", msp.std())

plt.figure(figsize=(8, 5))

plt.hist(
    msp,
    bins=30,
    density=True,
    edgecolor='black'
)

plt.axvline(
    msp.mean(),
    linestyle='--',
    label=f'Mean = {msp.mean():.2f}'
)

plt.xlabel('MSP [USD/kg]')
plt.ylabel('Probability density')
plt.title('Monte Carlo Distribution of MSP')
plt.legend()
plt.show()

# Spearman correlation plots 

print('\n MSP sensitivity\n')
df_rho, df_p = model.spearman_r()
print('\n Rho values\n', df_rho['-', 'MSP [USD/kg]'])
print('\n P values\n', df_p['-', 'MSP [USD/kg]'])
bst.plots.plot_spearman_1d(df_rho['-', 'MSP [USD/kg]'], index = [i.describe() for i in model.parameters], name = 'MSP [USD/kg]')
print('\n AOC sensitivity\n')
df_rho, df_p = model.spearman_r()
print('\n Rho values\n', df_rho['-', 'AOC [$/yr]'])
print('\n P values\n', df_p['-', 'AOC [$/yr]'])
bst.plots.plot_spearman_1d(df_rho['-', 'AOC [$/yr]'], index = [i.describe() for i in model.parameters], name = 'AOC [$/yr]')
print('\n NPV sensitivity\n')
df_rho, df_p = model.spearman_r()
print('\n Rho values\n', df_rho['-', 'NPV [$]'])
print('\n P values\n', df_p['-', 'NPV [$]'])
bst.plots.plot_spearman_1d(df_rho['-', 'NPV [$]'], index = [i.describe() for i in model.parameters], name = 'NPV [$]')
print('\n TCI sensitivity\n')
df_rho, df_p = model.spearman_r()
print('\n Rho values\n', df_rho['-', 'TCI [10^6*USD]'])
print('\n P values\n', df_p['-', 'TCI [10^6*USD]'])
bst.plots.plot_spearman_1d(df_rho['-', 'TCI [10^6*USD]'], index = [i.describe() for i in model.parameters], name = 'TCI [10^6*USD]')

# Single point sensitivity plots
baseline, lower, upper = model.single_point_sensitivity()
def plot_sps(metric, name, scale=1):

    metric_index = metric.index

    index = [
        i.describe(distribution=False)
        for i in model.parameters
    ]

    bst.plots.plot_single_point_sensitivity(
        scale * baseline[metric_index],
        scale * lower[metric_index],
        scale * upper[metric_index],
        name=name,
        index=index
    )

plot_sps(
    MSP,
    'MSP [USD/kg]',
    scale=1
)
plot_sps(
    TCI,
    'TCI [10^6*USD]',
    scale = 1
)
plot_sps(
    AOC,
    'AOC [$/yr]',
)
plot_sps(
    NPV,
    'NPV [$]',
    scale = 1
)