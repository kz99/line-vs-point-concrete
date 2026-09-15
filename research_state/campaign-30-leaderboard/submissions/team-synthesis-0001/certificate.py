"""Exact arithmetic replay for team-synthesis-0001.

This checks the finite identities and inequalities in the accompanying proof.
It uses no floating point and no randomness.  The analytic arguments remain in
note.md; this file is not a substitute for them.
"""

from fractions import Fraction as F
from math import comb, gcd


def ceiling(value: F) -> int:
    return (value.numerator + value.denominator - 1) // value.denominator


p = 147457
d = 87
h = p + 1
M = p * p
line_count = p * h
N = M * h
D = 15129
s = 5195
b = s - 1
q_der = D - d
A = 7349491214
recovery_count = 734949122

assert (M, line_count, N) == (21743566849, 21743714306, 3206262880419842)
assert p - 1 == 2**14 * 3**2
assert pow(10, p - 1, p) == 1
assert pow(10, (p - 1) // 2, p) == p - 1
assert pow(10, (p - 1) // 3, p) == 78348
assert gcd(pow(10, (p - 1) // 2, p) - 1, p) == 1
assert gcd(pow(10, (p - 1) // 3, p) - 1, p) == 1

monomials = sum(comb(D - d * z + 2, 2) for z in range(D // d + 1))
constraints = 3 * p * (D + 1)
assert (monomials, constraints, monomials - constraints) == (
    6693082347,
    6693073230,
    9117,
)

kappa = F(1610629120, 10871857153)
for accepted_degree in range(h + 1):
    missed = F(accepted_degree * comb(h - accepted_degree, 3), comb(h, 3))
    assert missed <= kappa * (h - accepted_degree)

max_z_degree = D // d
exceptional_cap = max(
    [D] + [(nu - 1) * (2 * D - d * nu) for nu in range(2, max_z_degree + 1)]
)
assert (max_z_degree, exceptional_cap) == (173, 2615604)

assert comb(b, 2) == 13486221
assert D * comb(42, 2) + 10956 * 42 == comb(b, 2)
assert D * comb(42, 2) + 10957 * 42 > comb(b, 2)
corner_edges = 42 * D + 10956
c4_credit = 2 * D * b - corner_edges
assert (corner_edges, c4_credit) == (646374, 156513678)
assert M + b * (D - 1) - c4_credit == 21665628003

fixed_charge = (
    (q_der + s - 1) * line_count
    + D * M
    + (p - q_der - s + 1) * exceptional_cap
    - c4_credit
)
assert fixed_charge == 769296828797543

frontier = (F(fixed_charge, N) + kappa) / (1 + kappa)
assert frontier == F(1244293905093223, 3681259956715522)
assert divmod(frontier.numerator * M, frontier.denominator) == (
    A - 1,
    548266597656141,
)

bar_epsilon = F(A, M)
bar_tau = bar_epsilon / 10
survival_loss = F(fixed_charge, N) + kappa * (1 - bar_epsilon)
assert bar_epsilon - survival_loss == F(1249813349, 27810935621062861282)

alpha = F(D + 1, h)
beta = F(s, p)
c = alpha / beta
gamma_squared = F(1, c * h)
endpoint = (beta - bar_tau) ** 2 - gamma_squared * (1 - bar_tau) * (1 - c * bar_tau)
endpoint_derivative = 2 * (bar_tau - beta) + gamma_squared * (1 + c - 2 * c * bar_tau)
assert endpoint == F(498727149435244, 30939665878432433176225)
assert endpoint_derivative == F(-13793284387, 4837976433085)

epsilon = F(3380076168821833, 10**16)
incidence_threshold = 1083741275308516
assert F(incidence_threshold - 1, N) < epsilon < frontier < F(incidence_threshold, N)
assert ceiling(N * epsilon) == incidence_threshold
assert ceiling(M * epsilon) == A
assert ceiling(M * epsilon / 10) == recovery_count
assert bar_tau > epsilon / 10 > F(174, p)
assert epsilon >= F(957, 10 * p)
assert ceiling(bar_tau * M) == recovery_count
assert 2 * d * p == 25657518

print("team-synthesis-0001 exact arithmetic: PASS")
