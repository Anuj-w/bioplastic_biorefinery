import biosteam as bst
from biosteam import units, Unit, Stream, main_flowsheet

system = main_flowsheet.create_system('Mulch_film_production')
system.converge_method = 'anderson'
system.maxiter = 120
system.molar_tolerance = 1e-4

system.simulate()
system.results()
system.show()
system.diagram(kind = 'thorough', format = 'png')
