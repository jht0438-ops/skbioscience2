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

div[data-testid="stLinkButton"] a{
    min-height:72px !important;
    font-size:20px !important;
    font-weight:800 !important;
    border-radius:14px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    padding:16px 28px !important;
}
div[data-testid="stLinkButton"] a p{
    font-size:20px !important;
    font-weight:800 !important;
}
</style>
""", unsafe_allow_html=True)

DATA=pd.DataFrame({"연도":[2023,2024,2025],"생산능력":[481,572,575],"생산실적":[269,215,201],"가동률":[55.9,37.6,35.0]})
DATA["미활용 생산능력"]=DATA["생산능력"]-DATA["생산실적"]
CAP,BASE,BASE_UTIL=575,201,35.0

defaults={"fixed":300.0,"variable":1.0,"base_prod":201,"scenario_prod":300,"yield_prod":201,"base_yield":80.0,"scenario_yield":90.0}
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
    intro(
        "고정제조원가는 생산량에 따라 각 Batch가 부담하는 금액이 달라질 수 있습니다.",
        "기준 생산량과 시나리오 생산량을 사용자가 직접 입력하고, 동일한 고정제조원가와 Batch당 변동비를 적용해 원가구조를 비교합니다.",
        "특정 연도의 실제 생산실적을 기준으로 고정하지 않고, 계획·예산·목표 등 분석 목적에 맞는 기준 생산량을 설정해 생산량 변화의 원가 영향을 확인합니다."
    )

    st.subheader("원가 가정 입력")
    c1,c2=st.columns(2)
    with c1:
        st.session_state.fixed=st.number_input("고정제조원가 (억원)",0.0,value=float(st.session_state.fixed),step=10.0)
    with c2:
        st.session_state.variable=st.number_input("Batch당 변동비 (억원/Batch)",0.0,value=float(st.session_state.variable),step=0.1)

    st.subheader("생산량 비교 설정")
    st.info("기준 생산량은 실제 생산실적에 고정된 값이 아니라, 사용자가 계획·예산·목표 등 분석 목적에 맞게 직접 설정하는 비교 기준입니다.")
    c1,c2=st.columns(2)
    with c1:
        st.session_state.base_prod=st.number_input("기준 생산량 (Batch)",1,CAP,int(st.session_state.base_prod),1)
    with c2:
        st.session_state.scenario_prod=st.number_input("시나리오 생산량 (Batch)",1,CAP,int(st.session_state.scenario_prod),1)

    bp,p=st.session_state.base_prod,st.session_state.scenario_prod
    f,v=st.session_state.fixed,st.session_state.variable
    b0,s=mfg(bp,f,v),mfg(p,f,v)
    unit_change=pct(s["unit"],b0["unit"]) if b0["unit"] else 0

    # 결과 요약: 기준과 시나리오를 한 박스 안에서 비교
    c1,c2,c3=st.columns(3)

    with c1:
        h,helpcol=st.columns([5,1])
        h.markdown("#### 가동률")
        with helpcol:
            with st.popover("❓"):
                st.markdown(
                    "**가동률 = 생산량 ÷ 생산능력 × 100**\n\n"
                    "본 시뮬레이터의 생산능력 분모는 **2025년 L HOUSE 공시 생산능력 575 Batch**로 고정합니다.\n\n"
                    "기준 생산량과 시나리오 생산량 모두 동일한 575 Batch를 분모로 사용합니다."
                )
        st.metric("기준 가동률",f"{b0['util']:.1f}%")
        st.metric("시나리오 가동률",f"{s['util']:.1f}%",f"{s['util']-b0['util']:+.1f}%p vs 기준")

    with c2:
        h,helpcol=st.columns([5,1])
        h.markdown("#### 미활용 생산능력")
        with helpcol:
            with st.popover("❓"):
                st.markdown(
                    "**미활용 생산능력 = 2025년 생산능력 575 Batch - 입력 생산량**\n\n"
                    "공시상 생산능력과 입력한 생산량의 단순 차이입니다. "
                    "즉시 추가 생산할 수 있는 물량이나 실제 유휴설비 규모를 의미하지 않습니다."
                )
        st.metric("기준 미활용 생산능력",f"{b0['unused']} Batch")
        st.metric("시나리오 미활용 생산능력",f"{s['unused']} Batch",f"{s['unused']-b0['unused']:+} Batch vs 기준")

    with c3:
        h,helpcol=st.columns([5,1])
        h.markdown("#### Batch당 제조원가")
        with helpcol:
            with st.popover("❓"):
                st.markdown(
                    "**Batch당 제조원가 = 고정제조원가 ÷ 생산량 + Batch당 변동비**\n\n"
                    "기준과 시나리오에 동일한 고정제조원가와 Batch당 변동비를 적용하여 "
                    "생산량 변화에 따른 고정비 배부 효과를 비교합니다."
                )
        st.metric("기준 Batch당 제조원가",f"{b0['unit']:.2f}억원")
        st.metric("시나리오 Batch당 제조원가",f"{s['unit']:.2f}억원",f"{unit_change:+.1f}% vs 기준")

    # 그래프는 '전체 제조원가'가 아니라 생산량에 따라 변하는 Batch당 고정비를 중심으로 표시.
    # 변동비는 생산량과 무관하게 Batch당 일정하므로 별도 기준선으로 표시.
    rng=np.arange(1,CAP+1)
    curve=pd.DataFrame({
        "생산량":rng,
        "Batch당 고정비":[mfg(x,f,v)["fixed_unit"] for x in rng]
    })

    left,right=st.columns([2,1])
    with left:
        fig=px.line(curve,x="생산량",y="Batch당 고정비")
        fig.add_hline(
            y=v,
            line_dash="dash",
            annotation_text=f"Batch당 변동비 {v:.2f}억원",
            annotation_position="top right"
        )
        fig.add_scatter(
            x=[bp,p],
            y=[b0["fixed_unit"],s["fixed_unit"]],
            mode="markers+text",
            text=[
                f"기준 {bp} Batch<br>{b0['fixed_unit']:.2f}억원",
                f"시나리오 {p} Batch<br>{s['fixed_unit']:.2f}억원"
            ],
            textposition="top center",
            name="선택값"
        )

        # 두 선택값이 화면 하단에 붙지 않도록 y축을 선택 구간 중심으로 자동 확대
        selected=[b0["fixed_unit"],s["fixed_unit"],v]
        ymin=min(selected)
        ymax=max(selected)
        pad=max((ymax-ymin)*0.45, max(ymax,1)*0.08)
        fig.update_yaxes(range=[max(0,ymin-pad), ymax+pad])
        fig.update_layout(
            xaxis_title="생산량 (Batch)",
            yaxis_title="억원 / Batch",
            title="생산량 변화에 따른 Batch당 고정비",
            legend_title=""
        )
        st.plotly_chart(fig,use_container_width=True)

    with right:
        st.markdown(f"""<div class="interpret"><b>💡 그래프 해석</b><br><br>
        이 그래프는 <b>생산량 변화에 직접 반응하는 Batch당 고정비</b>를 보여줍니다.<br><br>
        기준 생산량 <b>{bp} Batch</b>: Batch당 고정비 <b>{b0["fixed_unit"]:.2f}억원</b><br>
        시나리오 생산량 <b>{p} Batch</b>: Batch당 고정비 <b>{s["fixed_unit"]:.2f}억원</b><br><br>
        Batch당 변동비 <b>{v:.2f}억원</b>은 생산량이 바뀌어도 Batch당 금액이 일정하다고 가정하므로 점선으로 별도 표시합니다.<br><br>
        최종 Batch당 제조원가는 <b>Batch당 고정비 + Batch당 변동비</b>입니다.
        </div>""",unsafe_allow_html=True)

    st.markdown('<div class="warn"><b>⚠ 분석 시 유의사항</b><br>기준 생산량과 시나리오 생산량은 사용자 입력값입니다. 실제 생산량 변화 시 추가 인력·유지보수·원재료 단가·제품 믹스 등에 따라 원가구조가 달라질 수 있습니다.</div>',unsafe_allow_html=True)

with t3:
    st.header("03. 수율 변화에 따른 제조원가 분석")
    intro("동일한 생산량에서도 실제 확보하는 정상품에 따라 정상품 환산 기준 원가가 달라질 수 있습니다.",
          "2번 탭에서 입력한 고정제조원가·Batch당 변동비·생산량 시나리오로 총 제조원가를 계산하고, `생산량 × 수율`을 정상품 환산 생산량으로 단순화하여 원가를 분석합니다.",
          "같은 생산량에서 시나리오 수율이 기준 수율보다 높거나 낮을 때 정상품 환산 생산량과 정상품 환산 기준 제조원가가 어떻게 달라지는지 확인합니다.")
    h,helpcol=st.columns([5,1]); h.subheader("수율 가정 입력")
    with helpcol:
        with st.popover("❓ 어떻게 사용하나요?"):
            st.markdown("2번 탭에서 입력한 고정제조원가·Batch당 변동비·생산량 시나리오를 자동으로 불러옵니다. 총 제조원가는 `고정제조원가 + 생산량×Batch당 변동비`로 계산하며, `생산량×수율=정상품 환산 생산량`, `총 제조원가÷정상품 환산 생산량=정상품 환산 기준 제조원가`로 분석합니다. 시나리오 수율은 사용자가 입력하는 가정값입니다.")
    c1,c2,c3=st.columns(3)
    with c1:
        st.session_state.yield_prod = st.session_state.scenario_prod
        st.info(
            f"**분석 생산량**\n\n"
            f"### {st.session_state.yield_prod} Batch\n"
            f"2번 탭에서 입력한 **시나리오 생산량을 자동으로 불러온 값**입니다."
        )
    with c2: st.session_state.base_yield=st.number_input("기준 수율 (%)",1.0,100.0,float(st.session_state.base_yield),1.0)
    with c3:
        val=min(max(0.0,float(st.session_state.scenario_yield)),100.0)
        st.session_state.scenario_yield=st.number_input(
            "시나리오 수율 (%)",
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
    a,b,c,d,e=st.columns(5)
    a.metric("시나리오 수율",f"{iy:.0f}%",f"{iy-by:+.0f}%p vs 기준")
    b.metric("기준 수율 기준 정상품 환산 생산량",f"{y0['good']:.1f} Batch")
    c.metric("시나리오 수율 기준 정상품 환산 생산량",f"{y1['good']:.1f} Batch",f"{y1['good']-y0['good']:+.1f} Batch")
    d.metric("총 제조원가",f"{y1['total']:.1f}억원")
    e.metric("정상품 환산 기준 제조원가",f"{y1['unit']:.2f}억원",f"{unit_change:+.1f}%")
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
        생산량은 <b>{yp} Batch로 동일</b>하고, 시나리오 수율은 기준 수율 대비 <b>{by:.0f}% → {iy:.0f}% ({yield_direction})</b> 시나리오입니다.<br><br>
        정상품 환산 생산량은 <b>{y0["good"]:.1f} → {y1["good"]:.1f}</b>로 {good_direction}하고,
        정상품 환산 기준 제조원가는 <b>{y0["unit"]:.2f} → {y1["unit"]:.2f}억원</b>으로 {cost_direction}합니다.<br><br>
        <b>시나리오 수율이 기준보다 낮아지는 경우까지 포함해 원가 영향을 확인할 수 있습니다.</b></div>""",unsafe_allow_html=True)
    st.markdown('<div class="warn"><b>⚠ 분석 시 유의사항</b><br>실제 바이오 생산에서는 공정별 수율·투입량·품질검사·폐기·재작업 등이 영향을 미칩니다. 본 모델은 직관적 분석을 위한 단순화 모델입니다.</div>',unsafe_allow_html=True)

with t4:
    st.header("04. 생산량 × 수율 변화가 원가에 미치는 영향")
    intro(
        "생산량과 수율이 변할 때 정상품 1 Batch를 확보하는 데 드는 제조원가가 어떻게 움직이는지 한눈에 확인합니다.",
        "2번 탭의 기준·시나리오 생산량과 3번 탭의 기준·시나리오 수율을 결합해, 생산량 변화 효과와 수율 변화 효과를 순서대로 비교합니다.",
        "이 탭은 생산량과 수율에 초점을 둔 What-if 분석입니다. 실제 제조원가는 재료가격·재료사용량·작업시간·임률 등 다른 요인의 영향도 받으므로, 마지막에서 원가차이 분석 프로그램으로 이어집니다."
    )

    bp,sp=st.session_state.base_prod,st.session_state.scenario_prod
    by,ay=st.session_state.base_yield,st.session_state.scenario_yield
    f,v=st.session_state.fixed,st.session_state.variable

    base=ym(bp,by,f,v)
    prod_only=ym(sp,by,f,v)
    final=ym(sp,ay,f,v)

    prod_effect = pct(prod_only["unit"],base["unit"]) if base["unit"] else 0
    yield_effect = pct(final["unit"],prod_only["unit"]) if prod_only["unit"] else 0
    total_effect = pct(final["unit"],base["unit"]) if base["unit"] else 0

    st.info(
        "📌 **이 탭에서 보는 핵심 질문**  \n"
        "① 생산량이 바뀌면 고정비 배부 효과로 정상품 환산 기준 제조원가가 어떻게 변하는가?  \n"
        "② 그 생산량에서 수율까지 바뀌면 정상품 확보량과 원가는 추가로 어떻게 변하는가?"
    )

    # 1. 입력 조건을 먼저 보여줘 사용자가 무엇을 비교하는지 명확히 함
    st.subheader("① 무엇이 바뀌었는가?")

    c1,c2=st.columns(2)
    with c1:
        st.markdown(
            f"""<div class="interpret"><b>생산량 변화</b><br><br>
            기준 생산량 <b>{bp} Batch</b><br>
            ↓<br>
            시나리오 생산량 <b>{sp} Batch</b><br><br>
            변화: <b>{sp-bp:+} Batch</b>
            </div>""",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""<div class="interpret"><b>수율 변화</b><br><br>
            기준 수율 <b>{by:.0f}%</b><br>
            ↓<br>
            시나리오 수율 <b>{ay:.0f}%</b><br><br>
            변화: <b>{ay-by:+.0f}%p</b>
            </div>""",
            unsafe_allow_html=True
        )

    # 2. 변화 경로를 가장 중요한 그래프로 표시
    st.subheader("② 생산량과 수율이 바뀌면 원가는 어떻게 움직이는가?")

    stage=pd.DataFrame({
        "단계":[
            f"기준 조건\n{bp} Batch · 수율 {by:.0f}%",
            f"생산량 변경\n{sp} Batch · 수율 {by:.0f}%",
            f"수율까지 반영\n{sp} Batch · 수율 {ay:.0f}%"
        ],
        "정상품 환산 기준 제조원가":[base["unit"],prod_only["unit"],final["unit"]]
    })

    left,right=st.columns([2,1])
    with left:
        fig=px.line(
            stage,
            x="단계",
            y="정상품 환산 기준 제조원가",
            markers=True,
            text="정상품 환산 기준 제조원가"
        )
        fig.update_traces(texttemplate="%{text:.2f}억원",textposition="top center")
        vals=[base["unit"],prod_only["unit"],final["unit"]]
        ymin=min(vals); ymax=max(vals)
        pad=max((ymax-ymin)*0.55, max(ymax,1)*0.08)
        fig.update_yaxes(
            range=[max(0,ymin-pad),ymax+pad],
            title="억원 / 정상품 환산 Batch"
        )
        fig.update_xaxes(title="")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig,use_container_width=True)

    with right:
        prod_word="감소" if prod_effect < 0 else "증가" if prod_effect > 0 else "변화 없음"
        yield_word="감소" if yield_effect < 0 else "증가" if yield_effect > 0 else "변화 없음"
        total_word="감소" if total_effect < 0 else "증가" if total_effect > 0 else "변화 없음"

        # HTML 문자열을 사용하지 않고 Streamlit 기본 컴포넌트로 구성하여
        # <b>, <br> 태그가 화면에 그대로 노출되는 문제를 방지
        with st.container(border=True):
            st.markdown("### 💡 한눈에 보는 결과")

            st.markdown("**생산량 변화 효과**")
            st.metric(
                "생산량 변경 후 정상품 환산 기준 제조원가",
                f"{prod_only['unit']:.2f}억원",
                f"{prod_effect:+.1f}% vs 기준 {base['unit']:.2f}억원"
            )

            st.markdown("**수율 변화 추가 효과**")
            st.metric(
                "시나리오 수율 반영 후 정상품 환산 기준 제조원가",
                f"{final['unit']:.2f}억원",
                f"{yield_effect:+.1f}% vs 생산량 변경 후 {prod_only['unit']:.2f}억원"
            )

            st.markdown("**최종 변화**")
            st.metric(
                "기준 대비 최종 정상품 환산 기준 제조원가",
                f"{final['unit']:.2f}억원",
                f"{total_effect:+.1f}% vs 기준 {base['unit']:.2f}억원"
            )

    # 3. 왜 움직였는지 원인 경로 설명
    st.subheader("③ 왜 이렇게 움직였는가?")

    c1,c2=st.columns(2)
    with c1:
        st.markdown(
            f"""<div class="interpret"><b>생산량 → 고정비 배부 효과</b><br><br>
            Batch당 고정비<br>
            <b>{f/bp:.2f} → {f/sp:.2f}억원</b><br><br>
            생산량이 변하면 동일한 고정제조원가 <b>{f:.1f}억원</b>을 나누는 Batch 수가 달라집니다.
            따라서 Batch당 고정비가 변하고 제조원가에 영향을 줍니다.
            </div>""",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""<div class="interpret"><b>수율 → 정상품 확보 효과</b><br><br>
            동일한 {sp} Batch 생산 시 정상품 환산 생산량<br>
            <b>{prod_only["good"]:.1f} → {final["good"]:.1f} Batch</b><br><br>
            수율이 변하면 같은 생산량에서 확보되는 정상품 수가 달라집니다.
            총 제조원가를 나누는 정상품 환산 생산량이 달라져 정상품 기준 원가에 영향을 줍니다.
            </div>""",
            unsafe_allow_html=True
        )

    # 5. 다음 분석으로 자연스럽게 연결
    st.subheader("④ 생산량·수율만으로 설명되지 않는 원가는?")
    st.markdown(
        """<div class="warn"><b>생산량과 수율은 제조원가를 움직이는 일부 요인입니다.</b><br><br>
        실제 원가 차이는 원재료 가격, 실제 사용량, 작업시간, 임률 등에서도 발생할 수 있습니다.<br><br>
        따라서 다음 단계에서는 <b>가격차이·수량차이·능률차이·임률차이</b>를 분석하여
        계획 대비 실제 원가가 왜 달라졌는지 확인할 수 있습니다.
        </div>""",
        unsafe_allow_html=True
    )

    st.link_button(
        "➡️ 원가차이 분석 프로그램으로 이동",
        "https://skbs24-cg7wj6aw3zbfv9b5rhefcu.streamlit.app/",
        use_container_width=True
    )

with t5:
    st.header("05. Management Insight")
    intro("계산 결과를 실제 관리회계 의사결정으로 연결하기 위해 어떤 지표를 관리하고 계획과 실제가 달라질 때 무엇을 확인할지 정리합니다.",
          "앞선 탭의 생산능력·생산량·수율·제조원가 분석을 연결하여 현재와 목표 상태, 핵심 관리지표와 원가관리 프로세스를 정리합니다.",
          "생산량·수율·제조원가를 연결하고 실제 실적이 목표와 다르면 생산량→수율→세부 원가 순으로 점검하는 체계를 제시합니다.")
    fb=ym(st.session_state.base_prod,st.session_state.base_yield,st.session_state.fixed,st.session_state.variable)
    fs=ym(st.session_state.scenario_prod,st.session_state.scenario_yield,st.session_state.fixed,st.session_state.variable)
    final_unit_change=pct(fs["unit"],fb["unit"]) if fb["unit"] else 0
    summary=pd.DataFrame({
        "핵심지표":["생산량","가동률","미활용 생산능력","수율","정상품 환산 생산량","총 제조원가","정상품 환산 기준 제조원가"],
        "기준 조건":[f"{st.session_state.base_prod} Batch",f"{st.session_state.base_prod/CAP*100:.1f}%",f"{CAP-st.session_state.base_prod} Batch",f"{st.session_state.base_yield:.0f}%",f"{fb['good']:.1f}",f"{fb['total']:.1f}억원",f"{fb['unit']:.2f}억원"],
        "사용자 시나리오":[f"{st.session_state.scenario_prod} Batch",f"{st.session_state.scenario_prod/CAP*100:.1f}%",f"{CAP-st.session_state.scenario_prod} Batch",f"{st.session_state.scenario_yield:.0f}%",f"{fs['good']:.1f}",f"{fs['total']:.1f}억원",f"{fs['unit']:.2f}억원"]})
    st.subheader("L HOUSE 원가관리 Summary"); st.dataframe(summary,use_container_width=True,hide_index=True)
    st.markdown(f"""<div class="insight"><b>📌 Executive Summary</b><br><br>
    생산량 <b>{st.session_state.base_prod} → {st.session_state.scenario_prod} Batch</b>, 기준 수율 <b>{st.session_state.base_yield:.0f}%</b> 대비 시나리오 수율 <b>{st.session_state.scenario_yield:.0f}%</b> 가정 시 정상품 환산 기준 제조원가는 <b>{fb["unit"]:.2f} → {fs["unit"]:.2f}억원</b>으로 <b>{final_unit_change:+.1f}%</b> 변합니다.</div>""",unsafe_allow_html=True)
    st.subheader("그래서 무엇을 관리해야 하나요?")
    a,b,c=st.columns(3)
    a.markdown("### ① 생산량\n얼마나 생산했는가?\n\n`계획 생산량 vs 실제 생산량`")
    b.markdown("### ② 수율\n생산한 것 중 얼마나 확보했는가?\n\n`목표 수율 vs 시나리오 수율`")
    c.markdown("### ③ 제조원가\n결과적으로 얼마에 생산했는가?\n\n`목표 제조원가 vs 실제 제조원가`")
    st.subheader("관리회계 Cycle")
    st.markdown("""<div class="insight" style="text-align:center;"><b style="font-size:20px">PLAN → ACTUAL → VARIANCE → CAUSE → NEXT PLAN</b><br><br>
    <b>이번 프로그램</b><br>생산량·수율 시나리오 → 예상 제조원가 검토<br><br>↓ 실제 생산 ↓<br><br>
    <b>기존 원가차이 분석 프로그램</b><br>계획원가 vs 실제원가 → 차이 분석 → 원인 파악<br><br>↓<br><br><b>다음 생산계획에 반영</b></div>""",unsafe_allow_html=True)
    st.subheader("최종 Management Insight")
    st.markdown("""<div class="insight">제조원가 관리는 단순히 비용을 줄이는 것이 아니라 <b>생산계획과 생산성과를 원가 데이터로 연결하는 과정</b>입니다.<br><br>
    입사 후 실제 제품별 생산량·수율·원가 데이터를 활용하여 <b>계획 단계에서는 목표원가 달성 가능성을 검토하고, 생산 이후에는 계획과 실제의 차이를 분석해 다음 생산계획에 반영</b>하는 관리회계 업무를 수행하겠습니다.</div>""",unsafe_allow_html=True)
    st.markdown('<div class="warn"><b>⚠ 해석 원칙</b><br>생산량 확대나 특정 수율 달성을 지시하는 모델이 아니라 현업의 생산계획과 개선 시나리오를 재무적 효과로 환산해 의사결정을 지원하는 모델입니다.</div>',unsafe_allow_html=True)
