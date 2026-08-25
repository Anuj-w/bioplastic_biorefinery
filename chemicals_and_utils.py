import pandas as pd
import biosteam as bst
import thermosteam as tmo
from thermosteam import Chemical, Chemicals
from thermosteam.functional import rho_to_V


_cal2joule = 4.184
__all__ = ('create_chemicals', 'get_chemical_properties')
def create_chemicals(set_thermo = True):
    chems = Chemicals([])
    def add_chemical(ID, ref = None, **kwargs):
        chemical = Chemical(ID, **kwargs) if ref is None else ref.copy(ID, **kwargs)
        chems.append(chemical)
        return chemical
    Glucose = Chemical('Glucose')
    Water = add_chemical('Water')
    Vanillin = Chemical('Vanillin')
    LacticAcid = add_chemical('LacticAcid', Hfus = 11340)
    Lignin = add_chemical(
        'Lignin',
        search_db = False,
        phase = 's',
        formula = 'C9H10O2',
        Hf = -108248 * _cal2joule,
        default = True,
        )
    PLA = add_chemical(
        'PLA',
        search_db=False,
        phase='s',
        formula='C3H4O2',
        Hf=-150000*_cal2joule,
        default=True,
    )
    PEG400 = add_chemical(
        'PEG400',
        search_db=False,
        phase='l',
        formula='C18H38O10',
        MW=400,
        Hf=-200000*_cal2joule,
        default=True,
    )
    Mulch_film = add_chemical(
        'Mulch_film',
        search_db = False,
        phase = 's',
        formula = 'C3H4O2',
        Hf = -15000*_cal2joule,
        default = True
    )
    PEG400.copy_models_from(Glucose)
    PLA.copy_models_from(LacticAcid)
    Lignin.copy_models_from(Vanillin)
    Mulch_film.copy_models_from(LacticAcid)

    solid_density = 1540
    for chem in (
        Lignin,
        PLA,
        PEG400,
        Mulch_film
    ):
        chem.V.add_model(
            rho_to_V(solid_density, chem.MW),
            top_priority = True
        )
    for chem in chems:
        try:
            chem.default()
        except:
            pass
    chems.compile()
    if set_thermo: tmo.settings.set_thermo(chems)
    return chems

def get_chemical_properties(chemicals, T, P, output = False):
    formulas = [chemical.formula for chemical in chemicals]
    MW = [chemical.MW for chemical in chemicals]
    Hfs = [chemical.Hf for chemical in chemicals]
    HHVs = [chemical.HHV for chemical in chemicals]
    LHVs = [chemical.LHV for chemical in chemicals]
    phases = []
    Tbs = []
    Psats = []
    Vs = []
    Cns = []
    mus = []
    kappas = []

    for chemical in chemicals:
            if chemical.locked_state:
                phases.append(chemical.phase_ref)
                Tbs.append('NA')
                try: Psats.append(chemical.Psat(T=T, P=P))
                except: Psats.append('')
                try: Vs.append(chemical.V(T=T, P=P))
                except: Vs.append('')
                try: Cns.append(chemical.Cn(T=T))
                except: Cns.append('')
                try: mus.append(chemical.mu(T=T, P=P))
                except: mus.append('')
                try: kappas.append(chemical.kappa(T=T, P=P))
                except: kappas.append('')
            else:
                ref_phase = chemical.get_phase(T=T, P=P)
                phases.append(f'variable, ref={ref_phase}')
                Tbs.append(chemical.Tb)
                try: Psats.append(chemical.Psat(T=T, P=P))
                except: Psats.append('')
                try: Vs.append(chemical.V(ref_phase, T=T, P=P))
                except: Vs.append('')
                try: Cns.append(chemical.Cn(ref_phase, T=T))
                except: Cns.append('')
                try: mus.append(chemical.mu(ref_phase, T=T, P=P))
                except: mus.append('')
                try: kappas.append(chemical.kappa(ref_phase, T=T, P=P))
                except: kappas.append('')

    properties = pd.DataFrame(
            {'ID': chemicals.IDs,
            'formula': formulas,
            'MW': MW,
            'HHV': HHVs,
            'LHV': LHVs,
            'Hf': Hfs,
            'phase': phases,
            'boiling point': Tbs,
            'Psat': Psats,
            'V': Vs,
            'Cn': Cns,
            'mu': mus,
            'kappa': kappas}
            )

    if output:
        properties.to_excel('chemical_properties.xlsx', sheet_name='properties')

chems = create_chemicals()
bst.settings.CEPCI = 850
bst.settings.electricity_price = 0.1
steam_utility = bst.settings.get_agent('low_pressure_steam')
bst.settings.heating_agents = [steam_utility]
steam_utility.heat_transfer_efficiency = 0.8
steam_utility.T = 473.15
steam_utility.P = 22e5
steam_utility.regeneration_price = 10
bst.settings.get_agent('cooling_water').regeneration_price = 10
bst.units.PelletMill.reference_capacity = 5
units.PelletMill.purchase_cost = 1000
price = {
    'Lignin': 1.1,
    'PLA': 2.5,
    'PEG400': 2,
}

filler = bst.Stream(
    'filler',
    Lignin = 1000,
    phase = 's',
    units = 'kg/hr',
    price = price['Lignin']
)
polymer = bst.Stream(
    'polymer',
    PLA = 1000,
    phase = 's',
    units = 'kg/hr',
    price = price['PLA']
)
plasticizer = bst.Stream(
    'plasticizer',
    PEG400 = 80,
    phase = 's',
    units = 'kg/hr',
    price = price['PEG400']
)
