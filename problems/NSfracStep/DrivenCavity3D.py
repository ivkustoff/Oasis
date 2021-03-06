__author__ = "Mikael Mortensen <mikaem@math.uio.no>"
__date__ = "2013-06-25"
__copyright__ = "Copyright (C) 2013 " + __author__
__license__  = "GNU Lesser GPL version 3 or any later version"

from ..NSfracStep import *
from numpy import cos, pi

# Create a mesh
def mesh(Nx, Ny, Nz, **params):
    m = UnitCubeMesh(Nx, Ny, Nz)
    x = m.coordinates()
    x[:, :2] = (x[:, :2] - 0.5) * 2
    x[:, :2] = 0.5*(cos(pi*(x[:, :2]-1.) / 2.) + 1.)
    return m

# Override some problem specific parameters
NS_parameters.update(
    nu = 0.01,
    T  = 1.0,
    dt = 0.01,
    Nx = 15,
    Ny = 15,
    Nz = 15,
    plot_interval = 20,
    print_intermediate_info = 100,
    use_krylov_solvers = True)

class PeriodicDomain(SubDomain):

    def inside(self, x, on_boundary):
        # return True if on left or bottom boundary AND NOT on one of the two slave edges
        return bool(near(x[2], 0) and on_boundary)
                      
    def map(self, x, y):
        y[0] = x[0]
        y[1] = x[1] 
        y[2] = x[2] - 1.0
            
constrained_domain = PeriodicDomain()

# Specify boundary conditions
noslip = "std::abs(x[0]*x[1]*(1-x[0]))<1e-8"
top    = "std::abs(x[1]-1) < 1e-8"
def create_bcs(V, **NS_namespace):
    bc0  = DirichletBC(V, 0, noslip)
    bc00 = DirichletBC(V, 1, top)
    bc01 = DirichletBC(V, 0, top)
    return dict(u0 = [bc00, bc0],
                u1 = [bc01, bc0],
                u2 = [bc01, bc0],
                p  = [])
                
def initialize(x_1, x_2, bcs, **NS_namespace):
    for ui in x_2:
        [bc.apply(x_1[ui]) for bc in bcs[ui]]
        [bc.apply(x_2[ui]) for bc in bcs[ui]]

def pre_solve_hook(mesh, velocity_degree, constrained_domain, **NS_namespace):
    Vv = VectorFunctionSpace(mesh, 'CG', velocity_degree, constrained_domain=constrained_domain)
    return dict(Vv=Vv, uv=Function(Vv))

def temporal_hook(tstep, u_, Vv, uv, p_, plot_interval, **NS_namespace):
    if tstep % plot_interval == 0:
        assign(uv.sub(0), u_[0])
        assign(uv.sub(1), u_[1])
        assign(uv.sub(2), u_[2])
        plot(uv, title='Velocity')
        plot(p_, title='Pressure')

def theend_hook(u_, p_, uv, Vv, **NS_namespace):
    assign(uv.sub(0), u_[0])
    assign(uv.sub(1), u_[1])
    assign(uv.sub(2), u_[2])
    plot(uv, title='Velocity')
    plot(p_, title='Pressure')
