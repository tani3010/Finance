# -*- coding,  utf-8 -*-

USE_SYMENGINE = False

if USE_SYMENGINE:
    from symengine import Symbol
    from symengine import exp, sqrt
    from symengine import pi
    from symengine import series
else:
    from sympy import Symbol
    from sympy import exp, sqrt
    from sympy import pi
    from sympy import series

from sympy import init_printing
from sympy.core.cache import print_cache, clear_cache
from sympy import integrate, diff, Integral
from sympy import simplify
from sympy.printing.ccode import ccode
from sympy.printing.cxxcode import cxxcode
from sympy.printing.latex import latex
from sympy.printing.pycode import pycode
from sympy.printing.rcode import rcode
from func_timeout import func_timeout, FunctionTimedOut

class BaseWienerItoChaosExpansion:
    def __init__(self):
        init_printing(pretty_print=False)
        self.clear_cache()
        self.model_name = ''
        self.rr = Symbol('rr', positive=True)
        self.s = Symbol('s', positive=True)
        self.t = Symbol('t', positive=True)
        self.u = Symbol('u', positive=True)
        self.v = Symbol('v', positive=True)
        self.s0 = Symbol('s0')
        self.v0 = Symbol('v0', positive=True)
        self.rho = Symbol('rho')
        self.integrate_cond = 'none'
        self.degree_taylor_expansion = 3
        self.timeout_time = 8  # seconds
        self.simplify_flag = True
        self.cached_order = None
        self.cached_f_Xt = None
        self.cached_f_St = None
        self.event = None
        self.thread = None
        self.num_of_approx = 0

    def __del__(self):
        pass

    def clear_cache(self):
        self.cached_order = None
        self.cached_f_Xt = None
        self.cached_f_St = None
        clear_cache()

    @staticmethod
    def print_cache():
        print_cache()

    @staticmethod
    def clear_space_in_string(str):
        return str.replace(' ', '')

    @staticmethod
    def print_in_latex(expr):
        return latex(expr)

    @staticmethod
    def print_in_python(expr):
        return pycode(expr)

    @staticmethod
    def print_in_c(expr, standard='C99'):
        return ccode(expr, standard=standard)

    @staticmethod
    def print_in_cpp(expr, standard='c++11'):
        return cxxcode(expr, standard=standard)

    @staticmethod
    def print_in_r(expr):
        return rcode(expr)

    @staticmethod
    def write_expression_to_file(expr_string, file_name, num_columns=80):
        with open(file_name, mode='w') as f:
            i = 0
            while i <= len(expr_string):
                f.write(expr_string[i:(i+num_columns)])
                f.write('\n')
                i += num_columns

    @staticmethod
    def simplify2(expr):
        return simplify(expr)

    def simplify(self, expr):
        try:
            if self.simplify_flag:
                return func_timeout(self.timeout_time, simplify, args=(expr, ))
            else:
                return expr
        except FunctionTimedOut:
            print('simplify was canceled because spending too much time.')
            self.simplify_flag = False
            return expr
        except Exception as e:
            print('Unexpected Error was occured.')
            print(e)

    def series(self, expr, x, x0):
        return series(expr, x=x, x0=x0, n=self.degree_taylor_expansion)

    def integrate_symbolic(self, expr, int_range):
        return integrate(expr, int_range, conds=self.integrate_cond)

    def integrate_taylor(self, expr, int_range):
        return self.series(
            expr.subs({int_range[0]: int_range[2]}), int_range[2], int_range[1])

    def integrate(self, expr, int_range):
        try:
            return func_timeout(self.timeout_time, self.integrate_symbolic, args=(expr, int_range))
        except FunctionTimedOut:
            # self.num_of_approx += 1
            # print('symbolic integration was altered to approx. ' + str(self.num_of_approx))
            # return self.integrate_taylor(expr, int_range)
            print('The integration was aborted due to the time required.' + str(self.num_of_approx))
            return Integral(expr, int_range)
        except Exception as e:
            print('Unexpected Error was occured.')
            print(e)

    def r(self, t):
        pass

    def theta(self, t):
        pass

    def kappa(self, t):
        pass

    def sigma(self, s, v):
        pass

    def gamma(self, v):
        pass

    def F(self, t=Symbol('t', positive=True)):
        expr1_F = self.integrate(self.r(self.u), (self.u, 0, t))
        return self.s0 * exp(expr1_F)

    def E(self, t=Symbol('t', positive=True)):
        expr1_E = self.integrate(self.kappa(self.u), (self.u, 0, t))
        return exp(expr1_E)

    def Einv(self, t=Symbol('t', positive=True)):
        return 1 / self.E(t)

    def V(self, t=Symbol('t', positive=True)):
        expr1_V = self.Einv(t)
        expr2_V = self.integrate(self.E(self.u) * self.theta(self.u),
                                 (self.u, 0, t))
        return expr1_V * (self.v0 + expr2_V)

    def sigma0(self, t=Symbol('t', positive=True)):
        return self.simplify(self.sigma(self.F(t), self.V(t)))

    def sigma0_s(self, t=Symbol('t', positive=True)):
        expr1_sigma0_s = diff(self.sigma(Symbol('argS'), Symbol('argV')), 'argS', 1)
        expr2_sigma0_s = expr1_sigma0_s.subs({'argS': self.F(t), 'argV': self.V(t)})
        return self.simplify(expr2_sigma0_s)

    def sigma0_v(self, t=Symbol('t', positive=True)):
        expr1_sigma0_v = diff(self.sigma(Symbol('argS'), Symbol('argV')), 'argV', 1)
        expr2_sigma0_v = expr1_sigma0_v.subs({'argS': self.F(t), 'argV': self.V(t)})
        return self.simplify(expr2_sigma0_v)

    def sigma0_ss(self, t=Symbol('t', positive=True)):
        expr1_sigma0_ss = diff(self.sigma(Symbol('argS'), Symbol('argV')), 'argS', 2)
        expr2_sigma0_ss = expr1_sigma0_ss.subs({'argS': self.F(t), 'argV': self.V(t)})
        return self.simplify(expr2_sigma0_ss)

    def sigma0_sv(self, t=Symbol('t', positive=True)):
        expr1_sigma0_sv = diff(self.sigma(Symbol('argS'), Symbol('argV')), 'argS', 1)
        expr2_sigma0_sv = diff(expr1_sigma0_sv, 'argV', 1)
        expr3_sigma0_sv = expr2_sigma0_sv.subs({'argS': self.F(t), 'argV': self.V(t)})
        return self.simplify(expr3_sigma0_sv)

    def sigma0_vv(self, t=Symbol('t', positive=True)):
        expr1_sigma0_vv = diff(self.sigma(Symbol('argS'), Symbol('argV')), 'argV', 2)
        expr2_sigma0_vv = expr1_sigma0_vv.subs({'argS': self.F(t), 'argV': self.V(t)})
        return self.simplify(expr2_sigma0_vv)

    def gamma0(self, t=Symbol('t', positive=True)):
        return self.simplify(self.gamma(self.V(t)))

    def gamma0_v(self, t=Symbol('t', positive=True)):
        expr1_gamma0_v = self.gamma(Symbol('argV'))
        expr2_gamma0_v = diff(expr1_gamma0_v, 'argV', 1).subs({'argV': self.V(t)})
        return expr2_gamma0_v

    def p1(self, s=Symbol('s', positive=True)):
        expr1_p1 = self.sigma0(s)
        expr2_p1 = (self.simplify(
            self.sigma0_s(s) * self.F(s) + \
            0.5 * self.F(s) ** 2 * self.sigma0_ss(s))) * \
            self.integrate(self.sigma0(self.u) ** 2, (self.u, 0, s))
        expr3_p1 = self.simplify(
            0.5 * self.sigma0_vv(s) * self.Einv(s) ** 2) * \
            self.integrate(self.simplify(self.E(self.u) ** 2 * self.gamma0(self.u) ** 2),
                      (self.u, 0, s))
        expr4_p1 = (self.simplify(
            self.sigma0_v(s) * self.Einv(s) + \
            self.sigma0_sv(s) * self.F(s) * self.Einv(s))) * \
            self.integrate(
                self.rho * self.E(self.u) * self.gamma0(self.u) * self.sigma0(self.u),
                (self.u, 0, s))
        return self.simplify(expr1_p1 + expr2_p1 + expr3_p1 + expr4_p1)

    def p2(self, s=Symbol('s', positive=True)):
        return self.simplify(self.sigma0(s) + self.F(s) * self.sigma0_s(s))

    def p3(self, s=Symbol('s', positive=True)):
        return self.simplify(self.sigma0_v(s) * self.Einv(s))

    def p4(self, s=Symbol('s', positive=True)):
        return self.simplify(self.E(s) * self.gamma0(s))

    def p5(self, s=Symbol('s', positive=True)):
        return self.simplify(
                self.sigma0(s) + \
                3 * self.sigma0_s(s) * self.F(s) + \
                self.sigma0_ss(s) * self.F(s) ** 2)

    def p6(self, s=Symbol('s', positive=True)):
        return self.simplify(self.sigma0_vv(s) * self.Einv(s) ** 2)

    def p7(self, s=Symbol('s', positive=True)):
        return self.simplify(self.sigma0_v(s) * self.Einv(s) + \
                        self.sigma0_sv(s) * self.F(s) * self.Einv(s))

    def p8(self, s=Symbol('s', positive=True)):
        return self.simplify(self.sigma0_s(s) * self.F(s))

    def q21(self, t=Symbol('t', positive=True)):
        expr1_q21 = self.integrate(self.sigma0(self.rr) * self.p1(self.rr),
                                   (self.rr, 0, self.u))
        expr2_q21 = self.integrate(self.sigma0(self.u) * self.p1(self.u) * expr1_q21,
                                   (self.u, 0, self.s))
        expr3_q21 = self.integrate(self.p1(self.s) * self.p5(self.s) * expr2_q21,
                                   (self.s, 0, t))
        expr4_q21 = self.integrate(self.p1(self.u) * self.p8(self.u) * expr1_q21,
                                   (self.u, 0, self.s))
        expr5_q21 = self.integrate(self.p1(self.s) * self.p2(self.s) * expr4_q21,
                                   (self.s, 0, t))
        return self.simplify(expr3_q21 + expr5_q21)

    def q22(self, t=Symbol('t', positive=True)):
        expr1_q22 = self.integrate(self.rho * self.p1(self.rr) * self.p4(self.rr),
                                   (self.rr, 0, self.u))
        expr2_q22 = self.integrate(self.rho * self.p1(self.u) * self.gamma0_v(self.u) * expr1_q22,
                                   (self.u, 0, self.s))
        expr3_q22 = self.integrate(self.p1(self.s) * self.p3(self.s) * expr2_q22,
                                   (self.s, 0, t))
        return self.simplify(expr3_q22)

    def q23(self, t=Symbol('t', positive=True)):
        # term1
        expr1_q23 = self.integrate(self.rho * self.p1(self.rr) * self.p4(self.rr),
                                   (self.rr, 0, self.u))
        expr2_q23 = self.integrate(self.rho * self.p1(self.u) * self.p4(self.u) * expr1_q23,
                                   (self.u, 0, self.s))
        expr3_q23 = self.integrate(self.p1(self.s) * self.p6(self.s) * expr2_q23,
                                   (self.s, 0, t))

        # term2
        expr4_q23 = self.integrate(self.sigma0(self.rr) * self.p1(self.rr),
                                   (self.rr, 0, self.u))
        expr5_q23 = self.integrate(self.rho * self.p1(self.u) * self.p4(self.u) * expr4_q23,
                                   (self.u, 0, self.s))
        expr6_q23 = self.integrate(self.p1(self.s) * self.p7(self.s) * expr5_q23,
                                   (self.s, 0, t))

        # term3
        expr7_q23 = self.integrate(self.rho * self.p1(self.rr) * self.p4(self.rr),
                                   (self.rr, 0, self.u))
        expr8_q23 = self.integrate(self.sigma0(self.u) * self.p1(self.u) * expr7_q23,
                                   (self.u, 0, self.s))
        expr9_q23 = self.integrate(self.p1(self.s) * self.p7(self.s) * expr8_q23,
                                   (self.s, 0, t))

        # term4
        expr10_q23 = self.integrate(self.rho * self.p1(self.rr) * self.p4(self.rr),
                                    (self.rr, 0, self.u))
        expr11_q23 = self.integrate(self.p1(self.u) * self.p3(self.u) * expr10_q23,
                                    (self.u, 0, self.s))
        expr12_q23 = self.integrate(self.p1(self.s) * self.p2(self.s) * expr11_q23,
                                    (self.s, 0, t))

        return self.simplify(expr3_q23 + expr6_q23 + expr9_q23 + expr12_q23)

    def q41(self, t=Symbol('t', positive=True)):
        # term1
        expr1_q41 = self.integrate(self.sigma0(self.rr) ** 2,
                                   (self.rr, 0, self.u))
        expr2_q41 = self.integrate(self.p1(self.u) * self.p2(self.u) * expr1_q41,
                                   (self.u, 0, self.s))
        expr3_q41 = self.integrate(2 * self.p1(self.s) * self.p2(self.s) * expr2_q41,
                                   (self.s, 0, t))

        # term2
        expr4_q41 = self.integrate(self.sigma0(self.rr) * self.p1(self.rr),
                                   (self.rr, 0, self.u))
        expr5_q41 = self.integrate(self.sigma0(self.u) * self.p2(self.u) * expr4_q41,
                                   (self.u, 0, self.s))
        expr6_q41 = self.integrate(2 * self.p1(self.s) * self.p2(self.s) * expr5_q41,
                                   (self.s, 0, t))

        # term3
        expr7_q41 = self.integrate(self.sigma0(self.u) * self.p2(self.u),
                                   (self.u, 0, self.s))
        expr8_q41 = self.integrate(self.p2(self.s) ** 2 * expr7_q41 ** 2,
                                   (self.s, 0, t))

        return self.simplify(expr3_q41 + expr6_q41 + expr8_q41)

    def q42(self, t=Symbol('t', positive=True)):
        # term1
        expr1_q42 = self.integrate(self.p4(self.rr) ** 2,
                                   (self.rr, 0, self.u))
        expr2_q42 = self.integrate(self.p1(self.u) * self.p3(self.u) * expr1_q42,
                                   (self.u, 0, self.s))
        expr3_q42 = self.integrate(2 * self.p1(self.s) * self.p3(self.s) * expr2_q42,
                                   (self.s, 0, t))

        # term2
        expr4_q42 = self.integrate(self.rho * self.p1(self.rr) * self.p4(self.rr),
                                   (self.rr, 0, self.u))
        expr5_q42 = self.integrate(self.rho * self.p3(self.u) * self.p4(self.u) * expr4_q42,
                                   (self.u, 0, self.s))
        expr6_q42 = self.integrate(2 * self.p1(self.s) * self.p3(self.s) * expr5_q42,
                                   (self.s, 0, t))

        # term3
        expr7_q42 = self.integrate(self.rho * self.p1(self.u) * self.p4(self.u),
                                   (self.u, 0, self.s))
        expr8_q42 = self.integrate(self.p3(self.s) ** 2 * expr7_q42 ** 2,
                                   (self.s, 0, t))

        return self.simplify(expr3_q42 + expr6_q42 + expr8_q42)

    def q43(self, t=Symbol('t', positive=True)):
        # term1
        expr1_q43 = self.integrate(self.rho * self.sigma0(self.rr) * self.p4(self.rr),
                                   (self.rr, 0, self.u))
        expr2_q43 = self.integrate(self.p1(self.u) * self.p3(self.u) * expr1_q43,
                                   (self.u, 0, self.s))
        expr3_q43 = self.integrate(2 * self.p1(self.s) * self.p2(self.s) * expr2_q43,
                                   (self.s, 0, t))

        # term2
        expr4_q43 = self.integrate(self.rho * self.sigma0(self.rr) * self.p4(self.rr),
                                   (self.rr, 0, self.u))
        expr5_q43 = self.integrate(self.p1(self.u) * self.p2(self.u) * expr4_q43,
                                   (self.u, 0, self.s))
        expr6_q43 = self.integrate(2 * self.p1(self.s) * self.p3(self.s) * expr5_q43,
                                   (self.s, 0, t))

        # term3
        expr7_q43 = self.integrate(self.rho * self.p1(self.rr) * self.p4(self.rr),
                                   (self.rr, 0, self.u))
        expr8_q43 = self.integrate(self.sigma0(self.u) * self.p3(self.u) * expr7_q43,
                                   (self.u, 0, self.s))
        expr9_q43 = self.integrate(2 * self.p1(self.s) * self.p2(self.s) * expr8_q43,
                                   (self.s, 0, t))

        # term4
        expr10_q43 = self.integrate(self.sigma0(self.rr) * self.p1(self.rr),
                                    (self.rr, 0, self.u))
        expr11_q43 = self.integrate(self.rho * self.p2(self.u) * self.p4(self.u) * expr10_q43,
                                    (self.u, 0, self.s))
        expr12_q43 = self.integrate(2 * self.p1(self.s) * self.p3(self.s) * expr11_q43,
                                    (self.s, 0, t))

        # term5
        expr13_q43 = self.integrate(self.rho * self.p1(self.u) * self.p4(self.u),
                                    (self.u, 0, self.s))
        expr14_q43 = self.integrate(self.sigma0(self.u) * self.p1(self.u),
                                    (self.u, 0, self.s))
        expr15_q43 = self.integrate(2 * self.p2(self.s) * self.p3(self.s) * expr13_q43 * expr14_q43,
                                    (self.s, 0, t))

        return self.simplify(expr3_q43 + expr6_q43 + expr9_q43 + expr12_q43 + expr15_q43)

    def q1(self, t=Symbol('t', positive=True)):
        expr1_q1 = self.integrate(self.sigma0(self.u) * self.p1(self.u),
                                  (self.u, 0, self.s))
        expr2_q1 = self.integrate(self.p1(self.s) * self.p2(self.s) * expr1_q1,
                                  (self.s, 0, t))
        expr3_q1 = self.integrate(self.rho * self.p1(self.u) * self.p4(self.u),
                                  (self.u, 0, self.s))
        expr4_q1 = self.integrate(self.p1(self.s) * self.p3(self.s) * expr3_q1,
                                  (self.s, 0, t))
        return self.simplify(expr2_q1 + expr4_q1)

    def q2(self, t=Symbol('t', positive=True)):
        return self.simplify(self.q21(t) + self.q22(t) + self.q23(t))

    def q3(self, t=Symbol('t', positive=True)):
        return self.q1(t) **  2

    def q4(self, t=Symbol('t', positive=True)):
        return self.simplify(self.q41(t) + self.q42(t) + self.q43(t))

    def q5(self, t=Symbol('t', positive=True)):
        expr1_q5 = self.integrate(self.sigma0(self.u) ** 2,
                                  (self.u, 0, self.s))
        expr2_q5 = self.integrate(self.p2(self.s) ** 2 * expr1_q5,
                                  (self.s, 0, t))
        expr3_q5 = self.integrate(self.p4(self.u) ** 2,
                                  (self.u, 0, self.s))
        expr4_q5 = self.integrate(self.p3(self.s) ** 2 * expr3_q5,
                                  (self.s, 0, t))
        expr5_q5 = self.integrate(self.rho * self.sigma0(self.u) * self.p4(self.u),
                                  (self.u, 0, self.s))
        expr6_q5 = self.integrate(2 * self.p2(self.s) * self.p3(self.s) * expr5_q5,
                                  (self.s, 0, t))
        return self.simplify(expr2_q5 + expr4_q5 + expr6_q5)

    def Sigma(self, t=Symbol('t', positive=True)):
        return self.simplify(
                self.integrate(self.p1(self.s) ** 2, (self.s, 0, t)))

    def hermite(self, x=Symbol('x'), n=1):
        expr1_hermite = Symbol('x')
        expr2_hermite = (-1) ** n
        expr3_hermite = exp(0.5 * expr1_hermite ** 2)
        expr4_hermite = diff(exp(-0.5 * expr1_hermite ** 2), expr1_hermite, n)
        expr5_hermite = self.simplify(expr2_hermite * expr3_hermite * expr4_hermite)
        return expr5_hermite.subs([(expr1_hermite, x)])

    def n(self, x=Symbol('x'), Sigma=1):
        return 1 / sqrt(2 * pi * Sigma) * exp(-0.5 * x ** 2 / Sigma)

    def f_Xt(self, x=Symbol('x'), t=Symbol('t', positive=True), order=3,
             simplify=True, from_cache=True):
        if from_cache and self.cached_order == order and self.cached_f_Xt is not None:
            return self.cached_f_Xt

        expr1_f_xt = self.Sigma(t)
        expr2_f_xt = x / sqrt(expr1_f_xt)

        # coef
        expr3_f_xt = 0.5 * self.n(x, expr1_f_xt)

        if order <= 1:
            if simplify:
                output = self.simplify(expr3_f_xt * 2)
            else:
                output = expr3_f_xt * 2
            self.cached_order = order
            self.cached_f_Xt = output
            return output

        # term1
        expr4_f_xt = self.q3(t) / (expr1_f_xt ** 3) * self.hermite(expr2_f_xt, 6)

        # term2
        if order == 2:
            expr5_f_xt = self.q4(t) / (expr1_f_xt ** 2) * self.hermite(expr2_f_xt, 4)
        else:
            expr5_f_xt = (2 * self.q2(t) + self.q4(t)) / (expr1_f_xt ** 2) * self.hermite(expr2_f_xt, 4)

        # term3
        expr6_f_xt = 2 * self.q1(t) / (expr1_f_xt ** 1.5) * self.hermite(expr2_f_xt, 3)

        # term4
        expr7_f_xt = self.q5(t) / expr1_f_xt * self.hermite(expr2_f_xt, 2)

        if simplify:
            output = self.simplify(
                expr3_f_xt * (expr4_f_xt + expr5_f_xt + expr6_f_xt + expr7_f_xt + 2))
        else:
            output = expr3_f_xt * (expr4_f_xt + expr5_f_xt + expr6_f_xt + expr7_f_xt + 2)
        self.cached_order = order
        self.cached_f_Xt = output
        return output

    def f_St(self, x=Symbol('x'), t=Symbol('t', positive=True), order=3,
             simplify=True, from_cache=True):
        if from_cache and self.cached_order == order and self.cached_f_St is not None:
            return self.cached_f_St

        if simplify:
            output = self.simplify(self.f_Xt(x / self.F(t) - 1, t, order, simplify) / self.F(t))
        else:
            output = self.f_Xt(x / self.F(t) - 1, t, order, simplify, from_cache) / self.F(t)
        self.cached_order = order
        self.cached_f_St = output
        return output

    def show_model_spec(self):
        print('')
        print(' ====== {} ==========='.format(self.model_name))
        print(' ds(t)/s(t)  =  r(t)*dt+sigma(s, v)*dW_s(t)')
        print('             =  {}*dt+{}*dW_s(t)'.format(
                self.r(self.t), self.sigma(self.s, self.v)))
        print(' dv(t)       =  (theta(t)-kappa(t)*v)*dt+gamma(v)*dW_v(t)')
        print('             =  ({}-{}*v)*dt+{}*dW_v(t)'.format(
                self.theta(self.t), self.kappa(self.t), self.gamma(self.v)))
        print(' s(0)        = ', self.s0)
        print(' v(0)        = ', self.v0)
        print(' r(t)        = ', self.r(self.t))
        print(' sigma(s, v) = ', self.sigma(self.s, self.v))
        print(' theta(t)    = ', self.theta(self.t))
        print(' kappa(t)    = ', self.kappa(self.t))
        print(' gamma(v)    = ', self.gamma(self.v))
        print(' F(0, t)     = ', self.F(self.t))
        print(' E(t)        = ', self.E(self.t))
        print(' V(0, t)     = ', self.V(self.t))
        print('')