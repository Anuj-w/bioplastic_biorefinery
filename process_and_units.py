import biosteam as bst
from biosteam import units, Unit, Stream, main_flowsheet
from biosteam.units import Mixer, StorageTank, SolidsSeparator, HXutility
import numpy as np
import pandas as pd
from math import ceil
import matplotlib.pyplot as plt

class TwinScrewExtruder(bst.Unit):
    """
    Twin screw extruder for polymer/filler compounding.

    Parameters
    ----------
    ins :
        [0] Filler
        [1] Polymer
        [2] Plasticizer

    outs :
        Extruded pellets

    T :
        Operating temperature [K]

    P :
        Operating pressure [Pa]

    residence_time :
        Residence time [hr]

    specific_energy :
        Electricity consumption [kWh/kg]
    """

    _N_ins = 3
    _N_outs = 1

    _units = {
        'Throughput': 'kg/hr',
        'Power': 'kW',
        'Residence time': 'hr',
        'Temperature': 'K'
    }

    def _init(
            self,
            T=453.15,
            P=2e6,
            residence_time=0.05,
            specific_energy=0.20,
            screw_diameter=50,
            L_over_D=40,
            screw_speed=300,
            vent_moisture=True,
            moisture_removal=0.95,
            degradation=0.003,
            dispersion_efficiency=0.95,
            cooling_temperature=298.15,
            Cp=2.1,
    ):

        self.T = T
        self.P = P

        self.residence_time = residence_time
        self.specific_energy = specific_energy

        self.screw_diameter = screw_diameter
        self.L_over_D = L_over_D
        self.screw_speed = screw_speed

        self.vent_moisture = vent_moisture
        self.moisture_removal = moisture_removal

        self.degradation = degradation
        self.dispersion_efficiency = dispersion_efficiency

        self.cooling_temperature = cooling_temperature

        # average Cp of polymer melt
        self.Cp = Cp

    def _run(self):

        filler, polymer, plasticizer = self.ins

        strands = self.outs[0]

        strands.mix_from(self.ins)

        strands.T = self.T
        strands.P = self.P

        # Optional vacuum vent
        if self.vent_moisture:

            water = strands.imass['Water']

            removed = water * self.moisture_removal

            strands.imass['Water'] -= removed

        # Optional PLA degradation
        if 'PLA' in strands.chemicals:

            degraded = strands.imass['PLA'] * self.degradation

            strands.imass['PLA'] -= degraded

    def _design(self):

        strands = self.outs[0]

        throughput = strands.F_mass

        power = throughput * self.specific_energy

        self.design_results['Throughput'] = throughput

        self.design_results['Power'] = power

        self.design_results['Residence time'] = self.residence_time

        self.design_results['Temperature'] = self.T

        self.design_results['Screw diameter'] = self.screw_diameter

        self.design_results['L/D ratio'] = self.L_over_D

        self.design_results['Screw speed'] = self.screw_speed

        self.design_results['Dispersion efficiency'] = self.dispersion_efficiency

        self.power_utility(power)

        # Heating requirement

        Tin = max([i.T for i in self.ins])

        duty = throughput * self.Cp * (self.T - Tin)

        self.add_heat_utility(duty, self.T)

        # Cooling bath

        cooling = throughput * self.Cp * (self.T - self.cooling_temperature)

        self.add_heat_utility(-cooling, self.cooling_temperature)

    def _cost(self):

        throughput = self.design_results['Throughput']

        if throughput <=5:
            reference_capacity = 5
            reference_cost = 31500
        elif throughput <=500:
            reference_capacity = 500
            reference_cost = 31500*5
        else:
            reference_capacity = 1000
            reference_cost = 31500*10
        

        purchase_cost = reference_cost * (throughput/reference_capacity)**0.60        

        purchase_cost *= bst.settings.CEPCI / 567

        self.baseline_purchase_costs['Twin screw extruder'] = purchase_cost

        self.F_BM['Twin screw extruder'] = 2.3

class BlownFilmExtruder(bst.Unit):
    """
    Blown film extrusion.

    Parameters
    ----------
    ins :
        Polymer pellets

    outs :
        Film roll

    T :
        Melt temperature [K]

    film_thickness :
        Film thickness [mm]

    specific_energy :
        Electricity consumption [kWh/kg]
    """

    _N_ins = 1
    _N_outs = 1

    _units = {
        'Throughput': 'kg/hr',
        'Power': 'kW',
        'Temperature': 'K',
        'Film thickness': 'mm',
        'Film yield': '%',
    }

    def _init(
            self,
            T=453.15,
            film_thickness=0.05,
            specific_energy=0.15,
            film_yield = 0.98,
    ):

        self.T = T
        self.film_thickness = film_thickness
        self.specific_energy = specific_energy
        self.film_yield = film_yield

    def _run(self):

        feed = self.ins[0]
        film = self.outs[0]

        film.copy_like(feed)
        film.scale(self.film_yield)

        film.T = 298.15
        film.P = 101325

    def _design(self):

        throughput = self.outs[0].F_mass

        power = throughput * self.specific_energy

        self.design_results['Throughput'] = throughput
        self.design_results['Power'] = power
        self.design_results['Temperature'] = self.T
        self.design_results['Film thickness'] = self.film_thickness
        self.design_results['Film yield'] = self.film_yield

        self.power_utility(power)

    def _cost(self):

        throughput = self.design_results['Throughput']

        if throughput <=5:
            reference_capacity = 5
            reference_cost = 31500
        elif throughput <=500:
            reference_capacity = 500
            reference_cost = 31500*5
        else:
            reference_capacity = 1000
            reference_cost = 31500*10

        purchase_cost = reference_cost * (
            throughput / reference_capacity
        ) ** 0.60

        purchase_cost *= bst.settings.CEPCI / 567

        self.baseline_purchase_costs['Blown film extruder'] = purchase_cost

        self.F_BM['Blown film extruder'] = 2.3

class FilmWinder(bst.Unit):
    """
    Film winding unit.

    Parameters
    ----------
    ins :
        Continuous film from blown film extruder.

    outs :
        Wound film rolls.

    winding_speed :
        Film winding speed [m/min].

    roll_diameter :
        Finished roll diameter [m].

    specific_energy :
        Electricity consumption [kWh/kg film].
    """

    _N_ins = 1
    _N_outs = 1

    _units = {
        'Throughput': 'kg/hr',
        'Power': 'kW',
        'Winding speed': 'm/min',
        'Roll diameter': 'm',
    }

    def _init(
            self,
            winding_speed=60,
            roll_diameter=0.50,
            specific_energy=0.005,
    ):

        self.winding_speed = winding_speed
        self.roll_diameter = roll_diameter
        self.specific_energy = specific_energy

    def _run(self):

        film = self.ins[0]
        rolls = self.outs[0]

        # Simply copy incoming film
        rolls.copy_like(film)

    def _design(self):

        throughput = self.outs[0].F_mass

        power = throughput * self.specific_energy

        self.design_results['Throughput'] = throughput
        self.design_results['Power'] = power
        self.design_results['Winding speed'] = self.winding_speed
        self.design_results['Roll diameter'] = self.roll_diameter

        self.power_utility(power)

    def _cost(self):

        throughput = self.design_results['Throughput']

        if throughput <=5:
            reference_capacity = 5
            reference_cost = 1500
        elif throughput <=500:
            reference_capacity = 500
            reference_cost = 1500*5
        else:
            reference_capacity = 1000
            reference_cost = 1500*10

        purchase_cost = reference_cost * (
            throughput / reference_capacity
        ) ** 0.60

        purchase_cost *= bst.settings.CEPCI / 567

        self.baseline_purchase_costs['Film winder'] = purchase_cost

        self.F_BM['Film winder'] = 1.8

lignin_pla_filament = TwinScrewExtruder(
    'lignin_pla_filament',
    ins = [filler, polymer, plasticizer],
    outs = 'filament',
)
lignin_pla_pellet = units.PelletMill(
    'lignin_pla_pellet',
    ins = lignin_pla_filament.outs[0],
    outs = 'pellets', 
)
lignin_pla_film = BlownFilmExtruder(
    'lignin_pla_film',
    ins = lignin_pla_pellet.outs[0],
    outs = 'mulch_sheet',
)
film_bale = FilmWinder(
    'film_bale',
    ins = lignin_pla_film.outs[0],
)