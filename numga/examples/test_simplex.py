"""Some code for calculating the inertia maps of simplices in arbitrary dimensions"""

import numpy as np
from functools import lru_cache

from numga.backend.numpy.context import NumpyContext as Context


def simplex_inertia(B, C):
	"""inertia map given [N x n] barycentric weights and n corner points"""
	L = (C * B).sum(axis=1)
	s = 1 / L.norm().sqrt()     # make inertia proportional to norm of C, rather than C*C
	return (L * s).inertia_map().sum(axis=0)


@lru_cache()
def simplex_inertia_weights(N):
	"""Compute barycentric weighting matrix,
	mapping uniform density simplex,
	to its equivalent vertex-lumped-mass simplex
	"""
	D = np.eye(N) - 1 / N     # barycentric direction vectors from centroid to corners
	f = np.sqrt(1 / (1 + N))  # factor determining distance from centroid; tested for n=2,3,4
	B = 1 / N + D * f         # centroid barycentrics offset by f in direction of corners
	return B / N


def simplex_inertia_lumped(C):
	"""Inertia map of a uniform density simplex described by N corner points,
	described as antivectors as norm 1"""
	return simplex_inertia(simplex_inertia_weights(len(C)), C)


def simplex_inertia_brute(C):
	"""generate cube of sampling points; and pick sum(C) < 1"""
	n = 300
	N = len(C)
	s = np.linspace(0, 1, n + 1)
	s = (s[1:] + s[:-1]) / 2
	B = np.array(np.meshgrid(*[s]*(N-1), indexing='ij'))
	B = B.T.reshape(-1, (N-1))
	B = B[B.sum(axis=1) < 1]
	B = np.concatenate([B, (1-B.sum(axis=1, keepdims=True))], axis=1)

	return simplex_inertia(B, C / len(B))


def simplex_inertia_random(C):
	"""Simplex inertia via uniform random sampling of the simplex"""
	B = np.random.exponential(size=(100000, len(C)))
	return simplex_inertia(B / B.sum(axis=1, keepdims=True), C / len(B))


def test_simplex_line():
	ctx = Context('x+y+w0')
	M = ctx.multivector
	C = (M.x * [1, -1] + M.w * [1, 1]).dual()
	print('lumped')
	print(simplex_inertia_lumped(C).operator.axes)
	print(np.around(simplex_inertia_lumped(C).kernel, 2))
	print('brute')
	print(np.around(simplex_inertia_brute(C).kernel, 2))
	print(np.around(simplex_inertia_random(C).kernel, 2))


def test_simplex_triangle():
	ctx = Context('x+y+w0')
	M = ctx.multivector

	C = M.x * [1, -1, 0] + M.y * [0.5, 0.2, -1]

	C = (C + M.w).dual()
	print('lumped')
	print(np.around(simplex_inertia_lumped(C).kernel, 2))
	print('brute')
	print(np.around(simplex_inertia_brute(C).kernel, 2))


def test_simplex_tet():
	ctx = Context('x+y+z+w0')
	M = ctx.multivector

	C = M.x * [1, -1, 0, 2] + M.y * [0.5, 0.2, -1, -1] + M.z * [-0.5, 0.2, 0, -1]

	C = (C + M.w).dual()
	print('lumped')
	print(np.around(simplex_inertia_lumped(C).kernel, 2))
	print('brute')
	print(np.around(simplex_inertia_brute(C).kernel, 2))


