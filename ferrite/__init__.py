import sys
from .account import FerriteAccount, ferrite_account, sign_transaction_wrapper

def patch_web3():
    if "web3" in sys.modules:
        import web3
        web3.eth.account = ferrite_account
        print("ferrite-signer: Patched web3.eth.account with high-performance Rust core.")

patch_web3()