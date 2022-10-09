from level.core.machine_x86_64 import *

code = []

def abstract_code(f):
  def attach(*args):
    if f.__name__ in {'jnz_', 'jmp_', 'jz_'} and args[0] is None:
      raise Exception
    if f.__name__ == "fcomip_" and args[0] is None:
      raise Exception
    code.append((f.__name__, *args))

  return attach

def st(i):
  return i


@abstract_code
def int_():
  pass


@abstract_code
def syscall_():
  pass


@abstract_code
def lea_():
  pass


@abstract_code
def mov_():
  pass


@abstract_code
def movl_():
  pass


@abstract_code
def movb_():
  pass


@abstract_code
def mul_():
  pass


@abstract_code
def mulb_():
  pass


@abstract_code
def mull_():
  pass


@abstract_code
def mulq_():
  pass


@abstract_code
def imul_():
  pass


@abstract_code
def imulb_():
  pass


@abstract_code
def imull_():
  pass


@abstract_code
def div_():
  pass


@abstract_code
def divb_():
  pass


@abstract_code
def divl_():
  pass


@abstract_code
def idiv_():
  pass


@abstract_code
def idivb_():
  pass


@abstract_code
def idivl_():
  pass


@abstract_code
def not_():
  pass


@abstract_code
def neg_():
  pass


@abstract_code
def negb_():
  pass


@abstract_code
def negl_():
  pass


@abstract_code
def notb_():
  pass


@abstract_code
def notl_():
  pass


@abstract_code
def add_():
  pass


@abstract_code
def adc_():
  pass


@abstract_code
def addl_():
  pass


@abstract_code
def adcl_():
  pass


@abstract_code
def addb_():
  pass


@abstract_code
def adcb_():
  pass


@abstract_code
def sub_():
  pass


@abstract_code
def sbb_():
  pass


@abstract_code
def subl_():
  pass


@abstract_code
def sbbl_():
  pass


@abstract_code
def subb_():
  pass


@abstract_code
def sbbb_():
  pass


@abstract_code
def cmp_():
  pass


@abstract_code
def cmpl_():
  pass


@abstract_code
def cmpb_():
  pass


@abstract_code
def or_():
  pass


@abstract_code
def orl_():
  pass


@abstract_code
def orb_():
  pass


@abstract_code
def and_():
  pass


@abstract_code
def andl_():
  pass


@abstract_code
def andb_():
  pass


@abstract_code
def xor_():
  pass


@abstract_code
def xorl_():
  pass


@abstract_code
def xorb_():
  pass


@abstract_code
def bsr_():
  pass


@abstract_code
def ror_():
  pass


@abstract_code
def rorl_():
  pass


@abstract_code
def rorb_():
  pass


@abstract_code
def rol_():
  pass


@abstract_code
def roll_():
  pass


@abstract_code
def rolb_():
  pass


@abstract_code
def shl_():
  pass


@abstract_code
def shll_():
  pass


@abstract_code
def shlb_():
  pass


@abstract_code
def sal_():
  pass


@abstract_code
def sall_():
  pass


@abstract_code
def salb_():
  pass


@abstract_code
def shr_():
  pass


@abstract_code
def shrl_():
  pass


@abstract_code
def shrb_():
  pass


@abstract_code
def sar_():
  pass


@abstract_code
def sarl_():
  pass


@abstract_code
def sarb_():
  pass


@abstract_code
def call_():
  pass


@abstract_code
def ret_():
  pass


@abstract_code
def jump():
  pass


@abstract_code
def jmp_():
  pass


@abstract_code
def jz_():
  pass


@abstract_code
def jnz_():
  pass


@abstract_code
def dec_():
  pass


@abstract_code
def inc_():
  pass


@abstract_code
def setnz_():
  pass


@abstract_code
def setz_():
  pass


@abstract_code
def setns_():
  pass


@abstract_code
def sets_():
  pass


@abstract_code
def setc_():
  pass


@abstract_code
def setnc_():
  pass


@abstract_code
def setg_():
  pass


@abstract_code
def setge_():
  pass


@abstract_code
def setl_():
  pass


@abstract_code
def setle_():
  pass


@abstract_code
def seta_():
  pass


@abstract_code
def setae_():
  pass


@abstract_code
def setb_():
  pass


@abstract_code
def setbe_():
  pass


@abstract_code
def cmovl_():
  pass


@abstract_code
def cmovnl_():
  pass


@abstract_code
def cmovz_():
  pass


@abstract_code
def cmovnz_():
  pass


@abstract_code
def cmovs_():
  pass


@abstract_code
def cmovns_():
  pass


@abstract_code
def cmovg_():
  pass


@abstract_code
def push_():
  pass


@abstract_code
def pop_():
  pass


@abstract_code
def fildq_():
  pass


@abstract_code
def fldt_():
  pass


@abstract_code
def fld_():
  pass


@abstract_code
def fld1_():
  pass


@abstract_code
def fldl2t_():
  pass


@abstract_code
def fldl2e_():
  pass


@abstract_code
def fldpi_():
  pass


@abstract_code
def fldlg2_():
  pass


@abstract_code
def fldln2_():
  pass


@abstract_code
def fldz_():
  pass


@abstract_code
def fyl2x_():
  pass


@abstract_code
def fpatan_():
  pass


@abstract_code
def fldcw_():
  pass


@abstract_code
def fistpq_():
  pass


@abstract_code
def fbstp_():
  pass


@abstract_code
def fstpt_():
  pass


@abstract_code
def fstp_():
  pass


@abstract_code
def faddp_():
  pass


@abstract_code
def fsubp_():
  pass


@abstract_code
def fmulp_():
  pass


@abstract_code
def fdivp_():
  pass


@abstract_code
def fdivrp_():
  pass


@abstract_code
def fdiv_():
  pass


@abstract_code
def fchs_():
  pass


@abstract_code
def fabs_():
  pass


@abstract_code
def fsin_():
  pass


@abstract_code
def fcos_():
  pass


@abstract_code
def fsincos_():
  pass


@abstract_code
def fsqrt_():
  pass


@abstract_code
def f2xm1_():
  pass


@abstract_code
def fscale_():
  pass


@abstract_code
def fprem_():
  pass

@abstract_code
def fcomi_():
  pass


@abstract_code
def fcomip_():
  pass

@abstract_code
def begin():
  pass

@abstract_code
def entry():
  pass


@abstract_code
def set_symbol():
  pass


@abstract_code
def add_str():
  pass


@abstract_code
def add_bytes():
  pass


@abstract_code
def add_block():
  pass


@abstract_code
def set_cursor():
  pass


# @abstract_code
# def address():
#   pass