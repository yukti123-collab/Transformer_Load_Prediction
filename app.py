from pathlib import Path
import sys
import streamlit as st, pandas as pd, plotly.graph_objects as go, plotly.express as px
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from digital_twin.digital_twin import DigitalTwin
from integration.controller import run_automatic_simulation
st.set_page_config(page_title="Transformer Load Balancing",page_icon="⚡",layout="wide")
st.title("⚡ Transformer Load Balancing – Digital Twin Prototype")
st.caption("AI prediction • Automatic balancing algorithm • Simulated feeder transfer")
if "twin" not in st.session_state: st.session_state.twin=DigitalTwin()
if "result" not in st.session_state: st.session_state.result=None
twin=st.session_state.twin
with st.sidebar:
    st.header("Simulation controls"); hour=st.slider("Prediction hour",0,23,18); threshold=st.slider("Overload threshold (%)",50,100,80)
    st.info("Synthetic demonstration readings only. No physical equipment is controlled.")
    if st.button("Reset Digital Twin"):
        st.session_state.twin=DigitalTwin(); st.session_state.result=None; st.rerun()
net=twin.snapshot()
cols=st.columns(3)
for col,(f,v) in zip(cols,net.items()):
    peak=max(v[p] for p in ("R","Y","B")); col.metric(f,f"{peak/v['capacity']*100:.1f}% peak loading",f"{peak:.1f} A")
t1,t2,t3,t4=st.tabs(["2D Feeder Diagram","3D Digital Twin","AI + Algorithm","Results"])
with t1:
    st.subheader("Transformer → Busbar → Circuit breakers → Feeders")
    fig=go.Figure()
    fig.add_shape(type="rect",x0=.3,y0=2.1,x1=1.6,y1=2.9,fillcolor="#dce8f5",line=dict(width=2))
    fig.add_annotation(x=.95,y=2.5,text="TRANSFORMER",showarrow=False)
    fig.add_shape(type="line",x0=1.6,y0=2.5,x1=2.8,y1=2.5,line=dict(width=5,color="#607d8b"))
    fig.add_shape(type="line",x0=2.8,y0=.6,x1=2.8,y1=4.4,line=dict(width=7,color="#607d8b"))
    fig.add_annotation(x=2.8,y=4.65,text="MAIN BUSBAR",showarrow=False)
    for f,y in {"F1":3.8,"F2":2.5,"F3":1.2}.items():
        v=net[f]; peak=max(v[p] for p in ("R","Y","B")); c="#d9534f" if peak/v["capacity"]*100>=threshold else "#25865a"
        fig.add_shape(type="line",x0=2.8,y0=y,x1=3.8,y1=y,line=dict(width=3,color=c))
        fig.add_shape(type="rect",x0=3.8,y0=y-.17,x1=4.3,y1=y+.17,line=dict(width=2,color=c),fillcolor="white")
        fig.add_annotation(x=4.05,y=y,text="CB",showarrow=False,font=dict(color=c))
        fig.add_shape(type="line",x0=4.3,y0=y,x1=6,y1=y,line=dict(width=3,color=c))
        fig.add_annotation(x=6.1,y=y,text=f"{f} | {peak:.1f} A peak",showarrow=False,xanchor="left")
    fig.add_shape(type="line",x0=6,y0=3.8,x1=6,y1=1.2,line=dict(width=2,dash="dash",color="#9c755f"))
    fig.add_annotation(x=6,y=.75,text="SIMULATED TIE",showarrow=False)
    fig.update_layout(height=440,xaxis=dict(visible=False,range=[0,8]),yaxis=dict(visible=False,range=[.3,5]),margin=dict(l=5,r=5,t=20,b=5))
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(pd.DataFrame([{"Feeder":f,"R (A)":v["R"],"Y (A)":v["Y"],"B (A)":v["B"],"Breaker":v["breaker"]} for f,v in net.items()]).round(2),use_container_width=True,hide_index=True)
with t2:
    st.subheader("3D schematic Digital Twin")
    pts={"Transformer":(0,0,0),"Busbar":(2,0,0),"F1":(4,2,1),"F2":(4,0,0),"F3":(4,-2,-1)}
    ex=[];ey=[];ez=[]
    for a,b in [("Transformer","Busbar"),("Busbar","F1"),("Busbar","F2"),("Busbar","F3")]:
        for n in [pts[a],pts[b],(None,None,None)]: ex.append(n[0]);ey.append(n[1]);ez.append(n[2])
    fig=go.Figure(go.Scatter3d(x=ex,y=ey,z=ez,mode="lines",line=dict(color="#8295a8",width=7),hoverinfo="skip"))
    names=list(pts); colors=["#377eb8" if n in ("Transformer","Busbar") else ("#d9534f" if max(net[n][p] for p in ("R","Y","B"))/net[n]["capacity"]*100>=threshold else "#26966c") for n in names]
    fig.add_trace(go.Scatter3d(x=[pts[n][0] for n in names],y=[pts[n][1] for n in names],z=[pts[n][2] for n in names],text=names,mode="markers+text",textposition="top center",marker=dict(size=10,color=colors)))
    fig.update_layout(height=520,scene=dict(xaxis_title="X",yaxis_title="Y",zaxis_title="Level",aspectmode="data"),margin=dict(l=0,r=0,t=5,b=0))
    st.plotly_chart(fig,use_container_width=True)
    st.caption("Schematic 3D network, not CAD geometry or a validated electrical power-flow model.")
with t3:
    st.subheader("AI prediction and automatic load balancing")
    if st.button("▶ RUN AUTOMATIC SIMULATION",type="primary",use_container_width=True):
        with st.spinner("AI predicting feeder loads; algorithm calculating transfer..."):
            st.session_state.result=run_automatic_simulation(twin,hour,threshold)
        st.success("Digital Twin updated.")
    result=st.session_state.result
    if result:
        st.write("**AI Model – predicted next-hour phase currents**")
        st.dataframe(pd.DataFrame([{"Feeder":f,**{p+" (A)":v[p] for p in ("R","Y","B")}} for f,v in result["predictions"].items()]).round(2),use_container_width=True,hide_index=True)
        d=result["decision"]
        if d["transferred"]:
            st.success(f"Algorithm selected transfer: {d['source']} → {d['destination']}")
            st.write({p:f"{a:.2f} A" for p,a in d["phase_transfer"].items()})
        else: st.info(d["reason"])
    else: st.info("Press RUN AUTOMATIC SIMULATION to execute AI → algorithm → Digital Twin.")
with t4:
    result=st.session_state.result
    if result:
        data=[]
        for f in result["before"]:
            for p in ("R","Y","B"):
                data += [{"Feeder":f,"Phase":p,"Stage":"Before","Current (A)":result["before"][f][p]},{"Feeder":f,"Phase":p,"Stage":"After","Current (A)":result["after"][f][p]}]
        st.plotly_chart(px.bar(pd.DataFrame(data),x="Feeder",y="Current (A)",color="Stage",barmode="group",facet_col="Phase",title="Before vs after feeder phase currents"),use_container_width=True)
        st.dataframe(pd.DataFrame([{"Feeder":f,"After R":v["R"],"After Y":v["Y"],"After B":v["B"]} for f,v in result["after"].items()]).round(2),use_container_width=True,hide_index=True)
    else: st.info("Run the simulation to see before/after comparison.")
    st.markdown("**Digital Twin event log**")
    for event in reversed(twin.events): st.write("•",event)
st.divider()
st.caption("Educational prototype: synthetic data and simplified transfer logic. Real switching needs validated network topology, power-flow studies, protection coordination, interlocks and authorized engineering approval.")
