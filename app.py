import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="L HOUSE 생산성·원가 시뮬레이터", page_icon="📊", layout="wide")

st.markdown("""
<style>
.analysis{background:#f7f9fc;border:1px solid #e2e7ef;border-radius:12px;padding:18px;margin:12px 0 22px}
.interpret{background:#f8fafc;border-left:5px solid #64748b;border-radius:8px;padding:18px;line-height:1.75}
.warn{background:#fff8e8;border:1px solid #f2d28b;border-radius:10px;padding:16px;margin-top:14px}
.insight{background:#f3f8ff;border:1px solid #cddff5;border-radius:12px;padding:20px;line-height:1.8}
div[data-testid="stMetric"]{background:#fafafa;border:1px solid #eee;padding:14px;border-radius:10px}
</style>
""", unsafe_allow_html=True)

DATA=pd.DataFrame({"연도":[2023,2024,2025],"생산능력":[481,572,575],"생산실적":[269,215,201],"가동률":[55.9,37.6,35.0]})
DATA["미활용 생산능력"]=DATA["생산능력"]-DATA["생산실적"]
CAP,BASE,BASE_UTIL=575,201,35.0

defaults={"fixed":300.0,"variable":1.0,"scenario_prod":300,"yield_prod":201,"base_yield":80.0,"scenario_yield":90.0}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

def mfg(p,f,v):
    total=f+p*v
    return {"total":total,"fixed_unit":f/p,"unit":total/p,"util":p/CAP*100,"unused":CAP-p}

def ym(p,y,f,v):
    total=f+p*v; good=p*y/100
    return {"total":total,"good":good,"unit":total/good if good else 0}

def pct(n,o): return (n-o)/o*100 if o else 0

def intro(why,how,conclusion):
    st.markdown(f"""<div class="analysis"><b>왜 분석하나요?</b><br>{why}<br><br>
    <b>어떻게 분석하나요?</b><br>{how}<br><br>
    <b>이 탭을 통해 얻을 수 있는 결론은 무엇인가요?</b><br>{conclusion}</div>""",unsafe_allow_html=True)

st.title("L HOUSE 생산성·원가 시뮬레이터")
st.caption("생산능력 · 생산량 · 수율을 제조원가와 연결하여 L HOUSE의 생산성과 원가구조를 분석합니다.")
st.info("📌 생산능력·생산실적·가동률은 공개자료 기반이며, 수율·고정제조원가·Batch당 변동비·향후 생산량은 사용자 가정값입니다.")
st.caption("※ 정상품 환산 생산량 = 생산 Batch × 가정 수율로 단순화한 시뮬레이션 지표이며, 실제 완제품 생산량을 의미하지 않습니다.")

t1,t2,t3,t4,t5=st.tabs(["① L HOUSE 생산현황","② 생산량·원가 분석","③ 수율·원가 분석","④ 통합 시나리오","⑤ Management Insight"])

with t1:
    st.header("01. L HOUSE 생산현황 진단")
    intro(
        "SK바이오사이언스는 2026년 주요 계획으로 L HOUSE 생산수율 개선 및 cGMP Upgrade를 제시하고 있습니다. "
        "또한 2025년 L HOUSE G2+를 구축해 PCV21의 글로벌 상업생산 기반을 확대하고, "
        "R&D/제조 Infra Upgrade에 390억원을 투자했습니다. "
        "이러한 생산기반 확대 과정에서는 생산능력 확보뿐 아니라 실제 생산량과 수율 변화가 제조원가에 어떤 영향을 미치는지 "
        "관리회계 관점에서 점검할 필요가 있다고 보았습니다. "
        "이에 공개된 L HOUSE 생산능력·생산실적을 출발점으로 생산량과 수율 변화에 따른 원가구조를 분석합니다.\n\n"
        "※ PCV21의 실제 생산계획·수율·제조원가는 공개되지 않았으므로, 본 프로그램은 PCV21의 실제 원가를 추정하지 않고 "
        "L HOUSE 전체의 생산량·수율 변화에 따른 원가구조를 시뮬레이션합니다.",
        "먼저 2023~2025년 생산능력·생산실적·가동률을 비교합니다. 이후 생산량 변화는 가동률과 고정비 배부 변화, "
        "수율 변화는 정상품 환산 생산량 변화로 나누어 제조원가에 미치는 영향을 분석합니다.",
        "L HOUSE의 생산능력은 481→575 Batch로 증가한 반면 생산실적은 269→201 Batch로 감소했습니다. "
        "이를 생산 비효율로 단정하지 않고, 회사가 제시한 생산수율 개선 방향과 연결해 생산량·수율 변화가 제조원가 구조에 "
        "어떤 영향을 줄 수 있는지 다음 탭에서 시나리오로 확인합니다."
    )
    st.info(
        "📌 사업 맥락과 분석 구조\n\n"
        "L HOUSE 생산기반 확대·PCV21 상업생산 기반 구축 → "
        "생산량 변화: 가동률·고정비 배부 변화 + "
        "수율 변화: 정상품 환산 생산량 변화 → "
        "정상품 환산 기준 제조원가 변화\n\n"
        "본 분석은 PCV21의 실제 생산계획이나 원가를 예측하는 것이 아니라, "
        "회사가 공개한 생산성 개선 방향을 관리회계 관점의 시나리오로 연결한 것입니다."
    )
    a,b,c,d=st.columns(4)
    a.metric("2025 생산능력","575 Batch",f"{pct(575,481):+.1f}% vs 2023")
    b.metric("2025 생산실적","201 Batch",f"{pct(201,269):+.1f}% vs 2023")
    c.metric("2025 가동률","35.0%",f"{35-55.9:+.1f}%p vs 2023")
    d.metric("2025 미활용 생산능력","374 Batch")
    st.caption("※ 미활용 생산능력 = 공시상 생산능력 - 생산실적. 즉시 추가 생산 가능한 물량을 의미하지 않습니다.")
    left,right=st.columns([2,1])
    with left:
        x=DATA.melt(id_vars="연도",value_vars=["생산능력","생산실적"],var_name="구분",value_name="Batch")
        fig=px.bar(x,x="연도",y="Batch",color="구분",barmode="group",text_auto=True)
        fig.update_layout(xaxis=dict(tickmode="array",tickvals=[2023,2024,2025]),height=420)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("""<div class="interpret"><b>💡 그래프 해석</b><br><br>
        생산능력과 생산실적의 차이는 <b>212 → 357 → 374 Batch</b>로 확대되었습니다.<br><br>
        이는 생산설비 효율성을 단정하는 것이 아니라 공시상 생산능력 대비 실제 생산량의 차이가 확대된 현상을 보여줍니다.</div>""",unsafe_allow_html=True)
    st.dataframe(DATA,use_container_width=True,hide_index=True)
    left,right=st.columns([2,1])
    with left:
        fig=px.line(DATA,x="연도",y="가동률",markers=True,text="가동률")
        fig.update_traces(texttemplate="%{text:.1f}%",textposition="top center")
        fig.update_layout(xaxis=dict(tickmode="array",tickvals=[2023,2024,2025]),height=390)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown("""<div class="interpret"><b>💡 그래프 해석</b><br><br>
        가동률은 <b>55.9% → 37.6% → 35.0%</b>로 낮아졌습니다. 제품 수요·생산계획·제품 믹스·정기보수 등도 영향을 줄 수 있으므로 생산 비효율로 단정하지 않습니다.</div>""",unsafe_allow_html=True)

with t2:
    st.header("02. 생산량 변화에 따른 제조원가 분석")
    intro("고정제조원가는 생산량이 적을수록 각 생산단위의 부담이 커질 수 있습니다.",
          "201 Batch를 기준으로 고정제조원가와 Batch당 변동비를 입력하고 생산량 시나리오별 총 제조원가·Batch당 고정비·Batch당 제조원가를 계산합니다.",
          "필요 생산물량 증가 시 동일한 고정비가 더 많은 Batch에 배분되는 효과를 확인할 수 있습니다.")
    h,helpcol=st.columns([5,1])
    h.subheader("원가 가정 입력")
    with helpcol:
        with st.popover("❓ 어떻게 사용하나요?"):
            st.markdown("고정제조원가는 생산량과 직접 비례하지 않는 비용입니다. `고정비÷생산량`으로 Batch당 고정비를 계산합니다.\n\nBatch당 변동비는 Batch 수에 따라 증가한다고 가정합니다. 실제 회사 원가가 아닌 사용자 가정값입니다.")
    c1,c2=st.columns(2)
    with c1: st.session_state.fixed=st.number_input("연간 고정제조원가 (억원)",0.0,value=float(st.session_state.fixed),step=10.0)
    with c2: st.session_state.variable=st.number_input("Batch당 변동비 (억원/Batch)",0.0,value=float(st.session_state.variable),step=0.1)
    h,helpcol=st.columns([5,1]); h.subheader("생산량 시나리오")
    with helpcol:
        with st.popover("❓ 어떻게 사용하나요?"):
            st.markdown("2025년 공시 생산실적 201 Batch를 기준으로 What-if 생산량을 선택합니다. 선택값은 회사의 실제 계획이나 전망치가 아닙니다.")
    st.session_state.scenario_prod=st.slider("시나리오 생산량 (Batch)",BASE,CAP,int(st.session_state.scenario_prod))
    f,v,p=st.session_state.fixed,st.session_state.variable,st.session_state.scenario_prod
    b0,s=mfg(BASE,f,v),mfg(p,f,v); red=(b0["unit"]-s["unit"])/b0["unit"]*100
    a,b,c,d=st.columns(4)
    a.metric("생산량",f"{p} Batch",f"{p-BASE:+} Batch"); b.metric("가동률",f"{s['util']:.1f}%",f"{s['util']-BASE_UTIL:+.1f}%p")
    c.metric("미활용 생산능력",f"{s['unused']} Batch",f"{s['unused']-374:+} Batch"); d.metric("Batch당 제조원가",f"{s['unit']:.2f}억원",f"-{red:.1f}%")
    rng=np.arange(BASE,CAP+1)
    curve=pd.DataFrame({"생산량":rng,"Batch당 제조원가":[mfg(x,f,v)["unit"] for x in rng]})
    left,right=st.columns([2,1])
    with left:
        fig=px.line(curve,x="생산량",y="Batch당 제조원가")
        fig.add_scatter(x=[BASE,p],y=[b0["unit"],s["unit"]],mode="markers+text",text=["현재","시나리오"],textposition="top center",name="선택값")
        st.plotly_chart(fig,use_container_width=True)
    with right:
        st.markdown(f"""<div class="interpret"><b>💡 그래프 해석</b><br><br>
        생산량이 <b>201 → {p} Batch</b>로 증가하면 Batch당 고정비는 <b>{b0["fixed_unit"]:.2f} → {s["fixed_unit"]:.2f}억원</b>, Batch당 제조원가는 <b>{b0["unit"]:.2f} → {s["unit"]:.2f}억원</b>으로 변합니다.<br><br>
        <b>비용이 사라지는 것이 아니라 동일한 고정비를 더 많은 Batch가 나누어 부담하는 효과입니다.</b></div>""",unsafe_allow_html=True)
    st.markdown('<div class="warn"><b>⚠ 분석 시 유의사항</b><br>실제 생산량 증가 시 추가 인력·유지보수·원재료 단가·제품 믹스 등에 따라 원가구조가 달라질 수 있습니다.</div>',unsafe_allow_html=True)

with t3:
    st.header("03. 수율 변화에 따른 제조원가 분석")
    intro("동일한 생산량에서도 실제 확보하는 정상품에 따라 정상품 환산 기준 원가가 달라질 수 있습니다.",
          "2번 탭에서 입력한 고정제조원가·Batch당 변동비·생산량 시나리오로 총 제조원가를 계산하고, `생산량 × 수율`을 정상품 환산 생산량으로 단순화하여 원가를 분석합니다.",
          "같은 생산량에서 실제 수율이 기준 수율보다 높거나 낮을 때 정상품 환산 생산량과 정상품 환산 기준 제조원가가 어떻게 달라지는지 확인합니다.")
    h,helpcol=st.columns([5,1]); h.subheader("수율 가정 입력")
    with helpcol:
        with st.popover("❓ 어떻게 사용하나요?"):
            st.markdown("2번 탭에서 입력한 고정제조원가·Batch당 변동비·생산량 시나리오를 자동으로 불러옵니다. 총 제조원가는 `고정제조원가 + 생산량×Batch당 변동비`로 계산하며, `생산량×수율=정상품 환산 생산량`, `총 제조원가÷정상품 환산 생산량=정상품 환산 기준 제조원가`로 분석합니다. 실제 수율은 사용자가 입력하는 시나리오 값입니다.")
    c1,c2,c3=st.columns(3)
    with c1:
        st.session_state.yield_prod = st.session_state.scenario_prod
        st.metric("분석 생산량 (Batch)", f"{st.session_state.yield_prod} Batch")
        st.caption("※ 2번 탭의 생산량 시나리오를 자동으로 불러옵니다.")
    with c2: st.session_state.base_yield=st.number_input("기준 수율 (%)",1.0,100.0,float(st.session_state.base_yield),1.0)
    with c3:
        val=min(max(0.0,float(st.session_state.scenario_yield)),100.0)
        st.session_state.scenario_yield=st.number_input(
            "실제 수율 (%)",
            min_value=0.0,
            max_value=100.0,
            value=val,
            step=1.0
        )
    yp,by,iy=st.session_state.yield_prod,st.session_state.base_yield,st.session_state.scenario_yield
    linked_total_cost = st.session_state.fixed + yp * st.session_state.variable
    st.info(
        f"📌 2번 탭 연동 제조원가: 고정제조원가 {st.session_state.fixed:.1f}억원 "
        f"+ 생산량 {yp} Batch × Batch당 변동비 {st.session_state.variable:.2f}억원 "
        f"= 총 제조원가 {linked_total_cost:.1f}억원"
    )
    y0,y1=ym(yp,by,st.session_state.fixed,st.session_state.variable),ym(yp,iy,st.session_state.fixed,st.session_state.variable)
    unit_change=pct(y1["unit"],y0["unit"]) if y0["unit"] else 0
    a,b,c,d=st.columns(4)
    a.metric("실제 수율",f"{iy:.0f}%",f"{iy-by:+.0f}%p vs 기준"); b.metric("정상품 환산 생산량",f"{y1['good']:.1f}",f"{y1['good']-y0['good']:+.1f} Batch")
    c.metric("총 제조원가",f"{y1['total']:.1f}억원"); d.metric("정상품 환산 기준 제조원가",f"{y1['unit']:.2f}억원",f"{unit_change:+.1f}%")
    yr=np.arange(max(50,int(by)-20),101)
    curve=pd.DataFrame({"수율":yr,"정상품 환산 기준 제조원가":[ym(yp,y,st.session_state.fixed,st.session_state.variable)["unit"] for y in yr]})
    left,right=st.columns([2,1])
    with left:
        fig=px.line(curve,x="수율",y="정상품 환산 기준 제조원가")
        fig.add_scatter(x=[by,iy],y=[y0["unit"],y1["unit"]],mode="markers+text",text=["기준","실제"],textposition="top center",name="선택값")
        st.plotly_chart(fig,use_container_width=True)
    with right:
        yield_direction = "상승" if iy > by else "하락" if iy < by else "동일"
        good_direction = "증가" if y1["good"] > y0["good"] else "감소" if y1["good"] < y0["good"] else "동일"
        cost_direction = "증가" if y1["unit"] > y0["unit"] else "감소" if y1["unit"] < y0["unit"] else "변화 없음"
        st.markdown(f"""<div class="interpret"><b>💡 그래프 해석</b><br><br>
        생산량은 <b>{yp} Batch로 동일</b>하고, 실제 수율은 기준 수율 대비 <b>{by:.0f}% → {iy:.0f}% ({yield_direction})</b> 시나리오입니다.<br><br>
        정상품 환산 생산량은 <b>{y0["good"]:.1f} → {y1["good"]:.1f}</b>로 {good_direction}하고,
        정상품 환산 기준 제조원가는 <b>{y0["unit"]:.2f} → {y1["unit"]:.2f}억원</b>으로 {cost_direction}합니다.<br><br>
        <b>실제 수율이 기준보다 낮아지는 경우까지 포함해 원가 영향을 확인할 수 있습니다.</b></div>""",unsafe_allow_html=True)
    st.markdown('<div class="warn"><b>⚠ 분석 시 유의사항</b><br>실제 바이오 생산에서는 공정별 수율·투입량·품질검사·폐기·재작업 등이 영향을 미칩니다. 본 모델은 직관적 분석을 위한 단순화 모델입니다.</div>',unsafe_allow_html=True)

with t4:
    st.header("04. 생산량 × 수율 통합 시나리오")
    intro("실제 제조현장에서는 생산량과 수율이 동시에 변할 수 있으므로 두 효과를 함께 봅니다.",
          "현재 기준과 사용자 입력 시나리오를 비교하고 생산량 변화의 고정비 배분 효과와 실제 수율 변화의 정상품 환산 생산량 효과를 통합합니다.",
          "최종 정상품 환산 기준 제조원가 변화와 각 변화가 원가에 연결되는 경로를 확인합니다.")
    sp,by,sy=st.session_state.scenario_prod,st.session_state.base_yield,st.session_state.scenario_yield
    f,v=st.session_state.fixed,st.session_state.variable
    ib,vo,isc=ym(BASE,by,f,v),ym(sp,by,f,v),ym(sp,sy,f,v)
    ir=(ib["unit"]-isc["unit"])/ib["unit"]*100
    a,b,c,d=st.columns(4)
    a.metric("정상품 환산 생산량",f"{isc['good']:.1f}",f"{pct(isc['good'],ib['good']):+.1f}%")
    b.metric("총 제조원가",f"{isc['total']:.1f}억원",f"{pct(isc['total'],ib['total']):+.1f}%")
    c.metric("정상품 환산 기준 제조원가",f"{isc['unit']:.2f}억원",f"-{ir:.1f}%")
    d.metric("가동률",f"{sp/CAP*100:.1f}%",f"{sp/CAP*100-BASE_UTIL:+.1f}%p")
    st.subheader("단계별 원가 개선 효과")
    left,right=st.columns([2,1])
    with left:
        sdf=pd.DataFrame({"단계":["현재","생산량 변경 후","실제 수율 반영 후"],"정상품 환산 기준 제조원가":[ib["unit"],vo["unit"],isc["unit"]]})
        st.plotly_chart(px.bar(sdf,x="단계",y="정상품 환산 기준 제조원가",text_auto=".2f"),use_container_width=True)
    with right:
        st.markdown(f"""<div class="interpret"><b>💡 그래프 해석</b><br><br>
        <b>{ib["unit"]:.2f} → {vo["unit"]:.2f} → {isc["unit"]:.2f}억원</b>으로 변합니다.<br><br>
        생산량 변화는 고정비 배분에 영향을 주고, 실제 수율 변화는 같은 생산량에서 확보되는 정상품 환산 생산량에 영향을 줍니다.</div>""",unsafe_allow_html=True)
    st.caption("※ 생산량을 먼저 변경하고 수율을 이후 변경하는 순서의 단계별 분석이며 정확한 기여율 분해를 의미하지 않습니다.")
    st.subheader("생산량 × 수율 시나리오 매트릭스")
    prods=[201,250,300,350,400,450,500,575]; yields=[70,75,80,85,90,95,100]
    mat=pd.DataFrame(index=[f"{y}%" for y in yields],columns=prods,dtype=float)
    for y in yields:
        for p in prods: mat.loc[f"{y}%",p]=ym(p,y,f,v)["unit"]
    left,right=st.columns([2,1])
    with left:
        st.dataframe(mat.style.format("{:.2f}"),use_container_width=True)
        st.caption("단위: 억원 / 정상품 환산 Batch")
    with right:
        st.markdown("""<div class="interpret"><b>💡 매트릭스 해석</b><br><br>
        <b>→ 가로:</b> 생산량 증가의 고정비 분산 효과<br><br>
        <b>↓ 세로:</b> 수율 변화에 따른 정상품 환산 생산량 변화<br><br>
        <b>↘ 오른쪽 아래:</b> 두 변화가 동시에 발생하는 시나리오</div>""",unsafe_allow_html=True)

with t5:
    st.header("05. Management Insight")
    intro("계산 결과를 실제 관리회계 의사결정으로 연결하기 위해 어떤 지표를 관리하고 계획과 실제가 달라질 때 무엇을 확인할지 정리합니다.",
          "앞선 탭의 생산능력·생산량·수율·제조원가 분석을 연결하여 현재와 목표 상태, 핵심 관리지표와 원가관리 프로세스를 정리합니다.",
          "생산량·수율·제조원가를 연결하고 실제 실적이 목표와 다르면 생산량→수율→세부 원가 순으로 점검하는 체계를 제시합니다.")
    fb=ym(BASE,st.session_state.base_yield,st.session_state.fixed,st.session_state.variable)
    fs=ym(st.session_state.scenario_prod,st.session_state.scenario_yield,st.session_state.fixed,st.session_state.variable)
    final_unit_change=pct(fs["unit"],fb["unit"]) if fb["unit"] else 0
    summary=pd.DataFrame({
        "핵심지표":["생산량","가동률","미활용 생산능력","수율","정상품 환산 생산량","총 제조원가","정상품 환산 기준 제조원가"],
        "현재":[f"{BASE} Batch",f"{BASE_UTIL:.1f}%","374 Batch",f"{st.session_state.base_yield:.0f}%",f"{fb['good']:.1f}",f"{fb['total']:.1f}억원",f"{fb['unit']:.2f}억원"],
        "사용자 시나리오":[f"{st.session_state.scenario_prod} Batch",f"{st.session_state.scenario_prod/CAP*100:.1f}%",f"{CAP-st.session_state.scenario_prod} Batch",f"{st.session_state.scenario_yield:.0f}%",f"{fs['good']:.1f}",f"{fs['total']:.1f}억원",f"{fs['unit']:.2f}억원"]})
    st.subheader("L HOUSE 원가관리 Summary"); st.dataframe(summary,use_container_width=True,hide_index=True)
    st.markdown(f"""<div class="insight"><b>📌 Executive Summary</b><br><br>
    생산량 <b>{BASE} → {st.session_state.scenario_prod} Batch</b>, 기준 수율 <b>{st.session_state.base_yield:.0f}%</b> 대비 실제 수율 <b>{st.session_state.scenario_yield:.0f}%</b> 가정 시 정상품 환산 기준 제조원가는 <b>{fb["unit"]:.2f} → {fs["unit"]:.2f}억원</b>으로 <b>{final_unit_change:+.1f}%</b> 변합니다.</div>""",unsafe_allow_html=True)
    st.subheader("그래서 무엇을 관리해야 하나요?")
    a,b,c=st.columns(3)
    a.markdown("### ① 생산량\n얼마나 생산했는가?\n\n`계획 생산량 vs 실제 생산량`")
    b.markdown("### ② 수율\n생산한 것 중 얼마나 확보했는가?\n\n`목표 수율 vs 실제 수율`")
    c.markdown("### ③ 제조원가\n결과적으로 얼마에 생산했는가?\n\n`목표 제조원가 vs 실제 제조원가`")
    st.subheader("관리회계 Cycle")
    st.markdown("""<div class="insight" style="text-align:center;"><b style="font-size:20px">PLAN → ACTUAL → VARIANCE → CAUSE → NEXT PLAN</b><br><br>
    <b>이번 프로그램</b><br>생산량·수율 시나리오 → 예상 제조원가 검토<br><br>↓ 실제 생산 ↓<br><br>
    <b>기존 원가차이 분석 프로그램</b><br>계획원가 vs 실제원가 → 차이 분석 → 원인 파악<br><br>↓<br><br><b>다음 생산계획에 반영</b></div>""",unsafe_allow_html=True)
    st.subheader("최종 Management Insight")
    st.markdown("""<div class="insight">제조원가 관리는 단순히 비용을 줄이는 것이 아니라 <b>생산계획과 생산성과를 원가 데이터로 연결하는 과정</b>입니다.<br><br>
    입사 후 실제 제품별 생산량·수율·원가 데이터를 활용하여 <b>계획 단계에서는 목표원가 달성 가능성을 검토하고, 생산 이후에는 계획과 실제의 차이를 분석해 다음 생산계획에 반영</b>하는 관리회계 업무를 수행하겠습니다.</div>""",unsafe_allow_html=True)
    st.markdown('<div class="warn"><b>⚠ 해석 원칙</b><br>생산량 확대나 특정 수율 달성을 지시하는 모델이 아니라 현업의 생산계획과 개선 시나리오를 재무적 효과로 환산해 의사결정을 지원하는 모델입니다.</div>',unsafe_allow_html=True)
