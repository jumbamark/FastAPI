from ORM.calculations import add, subtract, multiply, divide, BankAccount, InsufficientFunds
import pytest


@pytest.mark.parametrize("num1, num2, result", [
    (3, 2, 5),
    (1, 1, 2),
    (12, 4, 16)
])
def test_add(num1, num2, result):
    sum = add(num1, num2)
    assert sum == result


def test_subtract():
    assert subtract(7, 3) == 4


def test_multiply():
    assert multiply(7, 3) == 21


def test_divide():
    print("testing add function")
    assert divide(27, 3) == 9


@pytest.fixture
def zero_bank_account():
    print("creating empty bank account")
    return BankAccount()


@pytest.fixture
def bank_account():
    return BankAccount(500)


def test_bank_default_amount(zero_bank_account):
    print("testing my bank account")
    assert zero_bank_account.balance == 0


def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 500


def test_withdraw():
    bank_account = BankAccount(1000)
    bank_account.withdraw(200)
    assert bank_account.balance == 800


def test_deposit():
    bank_account = BankAccount(1000)
    bank_account.deposit(2370)
    assert bank_account.balance == 3370


def test_collect_interest():
    bank_account = BankAccount(50)
    bank_account.collect_interest()
    assert round(bank_account.balance, 2) == 55


@pytest.mark.parametrize("deposited, withdrew, amount", [
    (200, 100, 100),
    (300, 50, 250),
    (2000, 450, 1550),
])
def test_bank_transaction(zero_bank_account, deposited, withdrew, amount):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == amount


def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds):
        bank_account.withdraw(800)
