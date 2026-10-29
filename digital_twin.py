from copy import deepcopy
import pandas as pd
DEFAULT_NETWORK={"F1":{"R":86.,"Y":78.,"B":82.,"capacity":100.,"breaker":"CLOSED"},
"F2":{"R":43.,"Y":48.,"B":45.,"capacity":100.,"breaker":"CLOSED"},
"F3":{"R":54.,"Y":50.,"B":52.,"capacity":100.,"breaker":"CLOSED"}}
class DigitalTwin:
    def __init__(self,network=None):
        self.network=deepcopy(network or DEFAULT_NETWORK); self.events=["Digital Twin initialized: transformer + 3 feeders."]
    def snapshot(self): return deepcopy(self.network)
    def update_feeder(self,f,currents):
        for p in ("R","Y","B"): self.network[f][p]=float(currents[p])
    def set_breaker(self,f,state): self.network[f]["breaker"]=state
    def apply_transfer(self,src,dst,transfer):
        for p in ("R","Y","B"):
            self.network[src][p]-=transfer[p]; self.network[dst][p]+=transfer[p]
        self.events.append(f"Simulated load transfer {src} → {dst}: "+", ".join(f"{p} {transfer[p]:.1f} A" for p in ("R","Y","B")))
