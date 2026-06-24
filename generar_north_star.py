#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador del North Star Dashboard de El Metodo · Automática.

Consulta GA4 (BigQuery) + la API de producción, calcula todas las métricas
y reescribe `north-star-dashboard.html` con datos reales y frescos.

Uso manual:   python3 generar_north_star.py
Programado:   lo lanza launchd cada mañana (ver north-star-dashboard.README.md).

Credenciales: se leen de ~/.config/elmetodo/dashboard.json (fuera del repo).
NO hay contraseñas en este archivo a propósito.
"""

import os, sys, json, html, socket, signal, warnings, urllib.request
from datetime import date, datetime, timedelta
from collections import defaultdict
from pathlib import Path

warnings.filterwarnings("ignore")  # silenciar avisos de Python 3.9 / urllib3
socket.setdefaulttimeout(60)       # ninguna conexión de red puede colgarse para siempre

# ───────────────────────── CONFIG ─────────────────────────
COHORTE          = "2026-05-11"   # arranque del onboarding nuevo
META_TRIMESTRE   = 3000           # meta de la North Star
META_ACTIVACION  = 35             # % objetivo
META_ENGANCHE    = 55             # % objetivo
META_COMPROMISO  = 25             # % objetivo

HERE      = Path(__file__).resolve().parent
OUT_HTML  = HERE / "north-star-dashboard.html"
SECRETS   = Path.home() / ".config" / "elmetodo" / "dashboard.json"
GA4_TABLE = "`automatica-v2.analytics_517999677.events_combined_mat`"

# nombre técnico del paso (GA4) -> etiqueta humana
STEP_LABELS = {
    "welcome": "Welcome", "video": "Vídeo intro", "personal_info": "Datos personales",
    "social_proof": "Prueba social", "objective": "Objetivo", "goal": "Objetivo concreto",
    "experience": "Nivel", "training_place": "Dónde entrenas", "days": "Días/semana",
    "program": "Programa recom.", "methodology": "Metodología", "register": "Registro",
    "health": "Salud", "notifications": "Notificaciones",
    "paywall": "Paywall", "pago": "→ Pago",
}

# ───────────────────────── helpers ─────────────────────────
def load_secrets():
    if not SECRETS.exists():
        sys.exit(f"ERROR: no encuentro las credenciales en {SECRETS}")
    return json.loads(SECRETS.read_text())

def pct(x, dec=0):
    s = f"{x:.{dec}f}".replace(".", ",")
    return s + "%"

def pct1(x):
    s = f"{x:.1f}".replace(".", ",")
    if s.endswith(",0"):
        s = s[:-2]
    return s + "%"

# ───────────────────────── GA4 ─────────────────────────
def ga4_client(key_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    from google.cloud import bigquery
    return bigquery.Client()

def q(client, sql):
    return list(client.query(sql, timeout=60).result(timeout=120))

def pp(key):
    # extrae un parámetro de evento de GA4 (sea string o int)
    return ("COALESCE("
            f"(SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key='{key}'),"
            f"CAST((SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key='{key}') AS STRING))")

def real_sessions_cte(days):
    # El evento training_session_complete se dispara MUCHAS veces por sesión real
    # (bug de instrumentación). Aquí lo deduplicamos: una sesión = (usuario, día,
    # programa, nombre de sesión), y solo cuenta como REAL si duró >=5 min, o si
    # falta la duración pero se hizo >=1 ejercicio (filtra el "curioseo": abrir y
    # darle a terminar sin entrenar).
    return f"""
      WITH ev AS (
        SELECT COALESCE(user_id, user_pseudo_id) AS u,
               DATE(TIMESTAMP_MICROS(event_timestamp)) AS d,
               {pp('program_id')} AS prog,
               {pp('day_name')} AS day_name,
               SAFE_CAST({pp('duration_seconds')} AS INT64) AS dur,
               SAFE_CAST({pp('exercises_completed')} AS INT64) AS ex
        FROM {GA4_TABLE}
        WHERE event_name='training_session_complete'
          AND DATE(TIMESTAMP_MICROS(event_timestamp)) >= DATE_SUB(CURRENT_DATE(), INTERVAL {days} DAY) ),
      sesiones AS (
        SELECT u, d, prog, day_name, MAX(dur) AS dur, MAX(ex) AS ex
        FROM ev
        WHERE dur >= 300 OR (dur IS NULL AND ex >= 1)
        GROUP BY u, d, prog, day_name )
    """

_MES = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]

def _derive_training(rows):
    """De las sesiones reales deduplicadas saca: North Star semanal, ventana 7d,
    rejilla semana×día, minutos por semana y el detalle de últimas sesiones."""
    sess = [(r.u, date.fromisoformat(r.d), r.prog, r.day_name, r.dur, r.ex) for r in rows]
    today = date.today()
    mon = lambda dt: dt - timedelta(days=dt.weekday())

    # North Star semanal = usuarios con >=2 sesiones reales esa semana
    wk_user = defaultdict(lambda: defaultdict(int))
    for u, dt, *_ in sess:
        wk_user[mon(dt)][u] += 1
    ns_weeks = [(w.isoformat(), sum(1 for n in us.values() if n >= 2))
                for w, us in sorted(wk_user.items())]

    def ns_window(lo, hi):
        c = defaultdict(int)
        for u, dt, *_ in sess:
            if lo <= dt <= hi:
                c[u] += 1
        return sum(1 for n in c.values() if n >= 2)
    ns_now  = ns_window(today - timedelta(days=6), today)
    ns_prev = ns_window(today - timedelta(days=13), today - timedelta(days=7))

    # agregados diario / semanal
    daily_u = defaultdict(set)
    wk_ses, wk_u, wk_dur = defaultdict(int), defaultdict(set), defaultdict(list)
    for u, dt, prog, dn, dur, ex in sess:
        daily_u[dt].add(u)
        m = mon(dt); wk_ses[m] += 1; wk_u[m].add(u)
        if dur is not None:
            wk_dur[m].append(dur)

    grid, base_mon = [], mon(today)
    for i in range(7, -1, -1):          # últimas 8 semanas
        m = base_mon - timedelta(weeks=i)
        days = [sorted(daily_u.get(m + timedelta(days=wd), set())) for wd in range(7)]
        ds = sorted(wk_dur.get(m, []))
        med = round(ds[len(ds)//2] / 60) if ds else None
        grid.append({"monday": m, "days": days, "ses": wk_ses.get(m, 0),
                     "users": len(wk_u.get(m, set())), "med_min": med})

    detail = [(dt, u, prog, dn, (round(dur/60) if dur else None), ex)
              for (u, dt, prog, dn, dur, ex) in sorted(sess, key=lambda x: x[1], reverse=True)[:30]]

    return {"ns_weeks": ns_weeks, "ns_now": ns_now, "ns_prev": ns_prev,
            "grid_weeks": grid, "detail": detail, "n_sesiones_30d": len(sess)}

def fetch_ga4(client):
    d = {}

    # Sesiones de entreno REALES y deduplicadas (ver real_sessions_cte). De aquí
    # salen North Star, rejilla diaria, minutos y detalle de sesiones.
    rows = q(client, real_sessions_cte(70) +
             " SELECT u, CAST(d AS STRING) AS d, prog, day_name, dur, ex FROM sesiones ")
    d.update(_derive_training(rows))

    # Embudo onboarding nuevo (usuarios distintos por hito) desde la cohorte
    rows = q(client, f"""
      SELECT
        COUNT(DISTINCT IF(event_name='onboarding_started', user_pseudo_id, NULL))               AS inicio,
        COUNT(DISTINCT IF(event_name='onboarding_recommendation_fetched', user_pseudo_id, NULL)) AS quiz,
        COUNT(DISTINCT IF(event_name='onboarding_register_success', user_pseudo_id, NULL))       AS registro,
        COUNT(DISTINCT IF(event_name='onboarding_purchase_completed', user_pseudo_id, NULL))     AS pago
      FROM {GA4_TABLE}
      WHERE DATE(TIMESTAMP_MICROS(event_timestamp)) >= '{COHORTE}' """)
    r = rows[0]
    d["funnel"] = {"inicio": r.inicio, "quiz": r.quiz, "registro": r.registro, "pago": r.pago}

    # Pasos del onboarding, ordenados por su posición REAL dentro del recorrido
    # de cada usuario (rango medio del 1er momento en que ve cada paso), no por
    # tiempo absoluto (que mezcla cohortes y descoloca la secuencia).
    rows = q(client, f"""
      WITH base AS (
        SELECT
          CASE
            WHEN event_name='onboarding_step_viewed'
              THEN (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key='step_name')
            WHEN event_name='onboarding_paywall_viewed'   THEN 'paywall'
            WHEN event_name='onboarding_purchase_completed' THEN 'pago'
          END AS step,
          user_pseudo_id, event_timestamp
        FROM {GA4_TABLE}
        WHERE DATE(TIMESTAMP_MICROS(event_timestamp)) >= '{COHORTE}'
          AND event_name IN ('onboarding_step_viewed','onboarding_paywall_viewed','onboarding_purchase_completed') ),
      first_seen AS (
        SELECT user_pseudo_id, step, MIN(event_timestamp) AS ts
        FROM base WHERE step IS NOT NULL GROUP BY user_pseudo_id, step ),
      ranked AS (
        SELECT step, user_pseudo_id,
               ROW_NUMBER() OVER (PARTITION BY user_pseudo_id ORDER BY ts) AS rn
        FROM first_seen )
      SELECT step, COUNT(DISTINCT user_pseudo_id) AS users, AVG(rn) AS avg_rank
      FROM ranked GROUP BY step ORDER BY avg_rank """)
    d["steps"] = [(r.step, r.users) for r in rows]

    # Palanca 1 · Activación: registrados (cohorte) con 1er entreno <=3 días del registro
    rows = q(client, f"""
      WITH reg AS (
        SELECT user_pseudo_id, MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS reg_d
        FROM {GA4_TABLE} WHERE event_name='onboarding_register_success'
          AND DATE(TIMESTAMP_MICROS(event_timestamp)) >= '{COHORTE}' GROUP BY user_pseudo_id ),
      tr AS (
        SELECT user_pseudo_id, MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) AS tr_d
        FROM {GA4_TABLE} WHERE event_name='training_session_complete' GROUP BY user_pseudo_id )
      SELECT COUNT(*) AS registrados,
             COUNTIF(tr.tr_d IS NOT NULL AND DATE_DIFF(tr.tr_d, reg.reg_d, DAY) BETWEEN 0 AND 3) AS activados
      FROM reg LEFT JOIN tr USING(user_pseudo_id) """)
    r = rows[0]
    d["activacion"] = {"base": r.registrados, "ok": r.activados}

    # Palanca 2 · Enganche social: % de activos (app_open 7d) que abren ranking (7d)
    rows = q(client, f"""
      SELECT
        COUNT(DISTINCT IF(event_name='app_open', user_pseudo_id, NULL)) AS activos,
        COUNT(DISTINCT IF(event_name IN ('ranking_filter_change','ranking_enrolled','ranking_tutorial_completed'),
                          user_pseudo_id, NULL)) AS ranking
      FROM {GA4_TABLE}
      WHERE DATE(TIMESTAMP_MICROS(event_timestamp)) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) """)
    r = rows[0]
    d["enganche"] = {"base": r.activos, "ok": r.ranking}
    return d

# ───────────────────────── API ─────────────────────────
def api_post(base, path, client_id, payload, token=None):
    req = urllib.request.Request(base + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", "X-Client-ID": client_id})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def api_get(base, path, client_id, token):
    req = urllib.request.Request(base + path, headers={"X-Client-ID": client_id, "Authorization": "Bearer " + token})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def fetch_api(s):
    token = api_post(s["api_base"], "/api/coaches/auth/login", s["api_client_id"],
                     {"email": s["api_email"], "password": s["api_password"]}).get("access_token", "")
    if not token:
        raise RuntimeError("login de la API falló (sin token)")
    ov = api_get(s["api_base"], "/api/dashboard/subscriptions/overview", s["api_client_id"], token)
    kpis = ov.get("kpis", {})
    tf = ov.get("trial_funnel", {})

    # mapa program_id -> nombre (para la tabla de sesiones)
    try:
        progs = api_get(s["api_base"], "/api/dashboard/programs?limit=500", s["api_client_id"], token)
        items = progs if isinstance(progs, list) else (
            progs.get("items") or progs.get("programs") or progs.get("data") or [])
        progmap = {str(p.get("id")): (p.get("title") or p.get("name") or "")
                   for p in items if p.get("id") is not None}
    except Exception:
        progmap = {}

    # mapa user_id -> {nombre, email} (roster paginado; el endpoint capa a 100/pág)
    usermap = {}
    try:
        page = 1
        while page <= 80:
            r = api_get(s["api_base"], f"/api/dashboard/subscriptions/users?page={page}&limit=100",
                        s["api_client_id"], token)
            us = r.get("users", [])
            for u in us:
                usermap[str(u.get("id"))] = {"name": u.get("name") or "", "email": u.get("email") or ""}
            if len(us) < 100:
                break
            page += 1
    except Exception:
        pass

    return {
        "trial_conversion": kpis.get("trial_conversion_rate", 0) or 0,
        "trials": tf.get("trial_started", 0) or 0,
        "mrr": kpis.get("mrr", 0) or 0,
        "subs_activos": kpis.get("total_active_subscribers", 0) or 0,
        "progmap": progmap,
        "usermap": usermap,
    }

# ───────────────────────── render ─────────────────────────
def build_spark(weeks):
    last = weeks[-6:] if len(weeks) >= 6 else weeks
    vals = [c for _, c in last]
    mx = max(vals) if vals and max(vals) > 0 else 1
    out = []
    for i, (_, c) in enumerate(last):
        h = max(round(c / mx * 100), 8)
        now = " now" if i == len(last) - 1 else ""
        out.append(f'          <div class="bar{now}" style="height:{h}%"><span>{c}</span></div>')
    return "\n".join(out)

def _user_label(u, usermap):
    """Devuelve (nombre, email) para una clave de usuario (user_id o pseudo_id)."""
    info = usermap.get(str(u))
    if info and (info.get("name") or info.get("email")):
        return info.get("name") or "—", info.get("email") or ""
    return "anónimo", f"id {str(u)[:12]}"

def _pop_html(dt, users, usermap):
    rows = []
    for u in users:
        nm, em = _user_label(u, usermap)
        rows.append(f'<div class="pop-u"><b>{html.escape(nm)}</b><span>{html.escape(em)}</span></div>')
    head = f'{dt.day:02d}-{_MES[dt.month-1]} · {len(users)} usuario(s)'
    return f'<div class="pop"><div class="pop-h">{head}</div>{"".join(rows)}</div>'

def build_grid(weeks, usermap):
    maxv = max((max((len(c) for c in w["days"]), default=0) for w in weeks), default=0) or 1
    head = "".join(f"<th>{x}</th>" for x in ["L", "M", "X", "J", "V", "S", "D"])
    out = [f'      <tr><th class="wk">semana</th>{head}<th class="wt">ses.</th><th class="wt">min</th></tr>']
    for w in reversed(weeks):                      # semana más reciente arriba
        cells = []
        for wd, cell_users in enumerate(w["days"]):
            v = len(cell_users)
            if v == 0:
                cells.append('<td><div class="dcell z"></div></td>')
            else:
                a = 0.20 + 0.80 * (v / maxv)
                dt = w["monday"] + timedelta(days=wd)
                pop = _pop_html(dt, cell_users, usermap)
                cells.append(f'<td><div class="dcell" style="background:rgba(79,70,229,{a:.2f})">{v}{pop}</div></td>')
        m = w["monday"]
        med = f'{w["med_min"]}′' if w["med_min"] else "—"
        out.append(f'      <tr><td class="wk">{m.day:02d}-{_MES[m.month-1]}</td>{"".join(cells)}'
                   f'<td class="wt">{w["ses"]}</td><td class="wt">{med}</td></tr>')
    return "\n".join(out)

def build_detail(detail, progmap, usermap):
    out = ['      <tr><th>Fecha</th><th>Usuario</th><th>Programa</th><th>Sesión</th><th class="r">Min</th><th class="r">Ejerc.</th></tr>']
    if not detail:
        out.append('      <tr><td colspan="6" style="color:var(--text-3)">sin sesiones reales en el periodo</td></tr>')
    for dt, u, prog, dn, mins, ex in detail:
        nm, em = _user_label(u, usermap)
        usr = f'<b>{html.escape(nm)}</b><span class="em">{html.escape(em)}</span>'
        pname = (progmap.get(str(prog)) if prog else None) or (f"#{prog}" if prog else "—")
        mlbl = f'{mins}′' if mins is not None else "—"
        out.append(f'      <tr><td>{dt.day:02d}-{_MES[dt.month-1]}</td><td class="usr">{usr}</td>'
                   f'<td>{html.escape(pname)}</td><td>{html.escape(dn or "—")}</td>'
                   f'<td class="r">{mlbl}</td><td class="r">{ex if ex is not None else "—"}</td></tr>')
    return "\n".join(out)

def build_steps(steps):
    if not steps:
        return ""
    first = max((u for _, u in steps), default=1) or 1
    rows, prev = [], None
    for i, (name, users) in enumerate(steps, 1):
        label = STEP_LABELS.get(name, name)
        w = round(users / first * 100)
        drop_txt, dcls, fcls = "", "", ""
        if prev is not None and prev > 0:
            drop = round((prev - users) / prev * 100)
            if drop >= 30:
                drop_txt, dcls, fcls = f"−{drop}%", " big", " bad"
            elif drop >= 10:
                drop_txt, dcls, fcls = f"−{drop}%", " mid", " warn"
            elif drop > 0:
                drop_txt = f"−{drop}%"
        rows.append(
            f'    <div class="srow"><div class="slabel">{i} · {label}</div>'
            f'<div class="strack"><div class="sfill{fcls}" style="width:{w}%">{users}</div></div>'
            f'<div class="sdrop{dcls}">{drop_txt}</div></div>')
        prev = users
    return "\n".join(rows)

def palanca_cls(val, meta):
    r = val / meta if meta else 0
    if r < 0.3:  return "bad"
    if r < 0.8:  return "warn"
    return ""

def render(d, api):
    f = d["funnel"]
    ini = f["inicio"] or 1
    c_quiz = f["quiz"] / ini * 100
    c_reg = f["registro"] / ini * 100
    c_pago = f["pago"] / ini * 100
    c_reg2pay = (f["pago"] / f["registro"] * 100) if f["registro"] else 0

    # North Star big + tendencia
    ns_now, ns_prev = d["ns_now"], d["ns_prev"]
    if ns_prev == 0:
        trend_txt, trend_cls = ("▲ nuevo" if ns_now > 0 else "— sin datos"), ("pos" if ns_now > 0 else "")
    else:
        ch = round((ns_now - ns_prev) / ns_prev * 100)
        if ch > 0:   trend_txt, trend_cls = f"▲ {ch}% vs 7d previos", "pos"
        elif ch < 0: trend_txt, trend_cls = f"▼ {abs(ch)}% vs 7d previos", ""
        else:        trend_txt, trend_cls = "→ estable vs 7d previos", "pos"
    prog = ns_now / META_TRIMESTRE * 100

    # palancas
    act = d["activacion"]; act_pct = (act["ok"] / act["base"] * 100) if act["base"] else 0
    eng = d["enganche"];   eng_pct = (eng["ok"] / eng["base"] * 100) if eng["base"] else 0
    com_pct = api["trial_conversion"]

    now = datetime.now()
    rep = {
        "@@UPDATED@@": f"actualizado {now.strftime('%d-%m-%Y')} · {now.strftime('%H:%M')} · GA4 + API",
        # hero
        "@@NS_BIG@@": str(ns_now),
        "@@NS_TREND@@": trend_txt,
        "@@NS_TREND_CLS@@": trend_cls,
        "@@NS_PROG@@": pct1(prog),
        "@@NS_PROG_W@@": f"{min(prog,100):.2f}%",
        "@@SPARK_BARS@@": build_spark(d["ns_weeks"]),
        "@@SPARK_CAP@@": "usuarios con ≥2 sesiones reales/sem · últimas 6 semanas",
        # entrenos · secciones nuevas
        "@@GRID_ROWS@@": build_grid(d["grid_weeks"], api.get("usermap", {})),
        "@@DETAIL_ROWS@@": build_detail(d["detail"], api.get("progmap", {}), api.get("usermap", {})),
        # embudo
        "@@F_INICIO@@": str(f["inicio"]), "@@F_QUIZ@@": str(f["quiz"]),
        "@@F_REG@@": str(f["registro"]), "@@F_PAGO@@": str(f["pago"]),
        "@@FW_QUIZ@@": f"{c_quiz:.0f}%", "@@FW_REG@@": f"{c_reg:.0f}%", "@@FW_PAGO@@": f"{c_pago:.1f}%",
        "@@FC_QUIZ@@": pct(c_quiz), "@@FC_REG@@": pct(c_reg), "@@FC_PAGO@@": pct1(c_pago),
        "@@FCONV@@": pct(c_reg), "@@FC_REG2PAY@@": pct(c_reg2pay),
        # pasos
        "@@N_STEPS@@": str(len(d["steps"])),
        "@@STEP_ROWS@@": build_steps(d["steps"]),
        # palancas
        "@@P1_VAL@@": pct1(act_pct), "@@P1_CLS@@": palanca_cls(act_pct, META_ACTIVACION),
        "@@P1_W@@": f"{min(act_pct/META_ACTIVACION*100,100):.0f}%",
        "@@P1_SUB@@": f"1er entreno en ≤3 días · {act['ok']}/{act['base']} registrados",
        "@@P2_VAL@@": pct1(eng_pct), "@@P2_CLS@@": palanca_cls(eng_pct, META_ENGANCHE),
        "@@P2_W@@": f"{min(eng_pct/META_ENGANCHE*100,100):.0f}%",
        "@@P2_SUB@@": f"abren ranking (7d) · sobre {eng['base']} activos",
        "@@P3_VAL@@": pct1(com_pct), "@@P3_CLS@@": palanca_cls(com_pct, META_COMPROMISO),
        "@@P3_W@@": f"{min(com_pct/META_COMPROMISO*100,100):.0f}%",
        "@@P3_SUB@@": f"trial → paid (API) · {api['trials']} trials",
        "@@META_ACT@@": f"&gt;{META_ACTIVACION}%", "@@META_ENG@@": f"&gt;{META_ENGANCHE}%",
        "@@META_COM@@": f"&gt;{META_COMPROMISO}%",
        "@@GOAL@@": f"{META_TRIMESTRE:,}".replace(",", "."),
    }
    html = TEMPLATE
    for k, v in rep.items():
        html = html.replace(k, str(v))
    return html

# ───────────────────────── main ─────────────────────────
def _abort(signum, frame):
    raise TimeoutError("la generación superó los 5 min (posible cuelgue de red); se aborta")

def main():
    # Tope absoluto: pase lo que pase, el proceso muere en <=5 min y nunca se
    # queda colgado bloqueando la ejecución del día siguiente.
    signal.signal(signal.SIGALRM, _abort)
    signal.alarm(300)
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] generando North Star Dashboard…")
    try:
        s = load_secrets()
        client = ga4_client(s["ga4_key_path"])
        d = fetch_ga4(client)
        api = fetch_api(s)
        html = render(d, api)
        OUT_HTML.write_text(html, encoding="utf-8")
        print(f"  North Star (≥2 entrenos/7d): {d['ns_now']}  (7d previos: {d['ns_prev']})")
        print(f"  Embudo: {d['funnel']}")
        print(f"  Activación {d['activacion']}  ·  Enganche {d['enganche']}  ·  trial→paid {api['trial_conversion']}%")
        print(f"  ✓ escrito {OUT_HTML}")
    except Exception as e:
        # No se reescribe el HTML: se conserva la última versión buena.
        print(f"  ✗ ERROR: {e}  — se conserva el HTML anterior")
        sys.exit(1)
    finally:
        signal.alarm(0)


# ───────────────────────── plantilla HTML ─────────────────────────
TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>North Star — Automática</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#f6f7f9; --card:#ffffff; --card-2:#fbfbfd;
    --border:#e8eaee; --border-2:#dfe2e8;
    --text-1:#0f172a; --text-2:#475569; --text-3:#94a3b8;
    --accent:#4f46e5; --accent-soft:#eef0fd; --accent-2:#6366f1;
    --pos:#16a34a; --pos-soft:#e8f6ed;
    --warn:#d97706; --warn-soft:#fef4e6;
    --danger:#dc2626; --danger-soft:#fdecec;
    --r:16px; --r-sm:12px; --r-pill:999px;
    --shadow:0 1px 2px rgba(16,24,40,.04), 0 4px 16px rgba(16,24,40,.05);
    --shadow-sm:0 1px 2px rgba(16,24,40,.05);
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{
    font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text-1);
    -webkit-font-smoothing:antialiased;padding:40px 28px 72px;line-height:1.5;
    background-image:radial-gradient(800px 400px at 85% -5%, rgba(79,70,229,.05), transparent 60%);
  }
  .wrap{max-width:1180px;margin:0 auto}

  /* header */
  .top{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin-bottom:28px}
  .eyebrow{font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
  h1{font-size:32px;font-weight:800;letter-spacing:-.025em}
  .updated{font-size:12px;color:var(--text-3);font-weight:500;white-space:nowrap}

  .meta{font-size:14.5px;color:var(--text-3);margin-bottom:20px}
  .meta b{color:var(--text-2);font-weight:600}

  /* north star hero */
  .hero{position:relative;background:var(--card);border:1px solid var(--border);border-radius:20px;
    padding:32px 34px;margin-bottom:28px;box-shadow:var(--shadow);overflow:hidden}
  .hero::before{content:"";position:absolute;inset:0;background:radial-gradient(540px 220px at 8% -20%,rgba(79,70,229,.07),transparent 70%);pointer-events:none}
  .hero-grid{position:relative;display:grid;grid-template-columns:1.1fr .9fr;gap:30px;align-items:center}
  @media(max-width:760px){.hero-grid{grid-template-columns:1fr}}
  .star-label{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:600;color:var(--accent);
    letter-spacing:.04em;margin-bottom:8px;background:var(--accent-soft);padding:5px 11px;border-radius:var(--r-pill)}
  .star-name{font-size:34px;font-weight:800;letter-spacing:-.02em;margin-bottom:5px}
  .star-def{font-size:14px;color:var(--text-3);max-width:430px}
  .star-num{display:flex;align-items:baseline;gap:14px;margin:20px 0 8px}
  .big{font-size:72px;font-weight:800;letter-spacing:-.04em;line-height:.9;color:var(--text-1)}
  .trend{font-size:13px;font-weight:600;color:var(--danger);background:var(--danger-soft);padding:6px 12px;border-radius:var(--r-pill)}
  .trend.pos{color:var(--pos);background:var(--pos-soft)}
  .star-foot{font-size:13px;color:var(--text-3)}
  .star-foot .amber{color:var(--warn);font-weight:600}
  .progress{height:8px;border-radius:var(--r-pill);background:#eef0f3;overflow:hidden}
  .progress i{display:block;height:100%;border-radius:var(--r-pill);background:linear-gradient(90deg,var(--accent-2),var(--accent))}
  .progress.warn i{background:linear-gradient(90deg,#f6c343,var(--warn))}
  /* spark */
  .spark{display:flex;align-items:flex-end;gap:9px;height:128px;padding-top:10px}
  .spark .bar{flex:1;background:#e6e1fb;border-radius:6px 6px 3px 3px;min-height:8px;position:relative}
  .spark .bar.now{background:linear-gradient(180deg,var(--accent-2),var(--accent))}
  .spark .bar.old{background:#e9ebf0}
  .spark .bar span{position:absolute;top:-19px;left:50%;transform:translateX(-50%);font-size:10.5px;color:var(--text-3);font-weight:500}
  .spark-cap{font-size:11.5px;color:var(--text-3);text-align:center;margin-top:12px}

  /* section title */
  .sec{font-size:12.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--text-3);margin:0 0 16px}
  .sec .ok{color:var(--pos)}

  /* paneles de entreno (rejilla diaria + tabla de sesiones) */
  .panel{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:18px 20px;margin-bottom:34px;box-shadow:var(--shadow-sm);overflow-x:auto}
  .panel-note{font-size:11px;color:var(--text-3);margin-top:14px;line-height:1.55}
  .panel-note b{color:var(--text-2);font-weight:600}
  .dgrid{width:100%;border-collapse:separate;border-spacing:4px}
  .dgrid th{font-size:10.5px;font-weight:600;color:var(--text-3);text-transform:uppercase;text-align:center;padding:2px 0}
  .dgrid th.wk,.dgrid td.wk{text-align:left;white-space:nowrap}
  .dgrid td.wk{font-size:11.5px;color:var(--text-2);padding-right:10px}
  .dgrid td.wt{font-size:12.5px;font-weight:700;color:var(--text-2);text-align:center}
  .dgrid th.wt{color:var(--text-3)}
  .dcell{position:relative;height:30px;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:12px;font-weight:700;cursor:default}
  .dcell.z{background:#f1f3f6}
  /* popover al pasar el ratón por una celda */
  .panel.pop-ok{overflow:visible}
  .pop{display:none;position:absolute;z-index:30;top:calc(100% + 7px);left:50%;transform:translateX(-50%);
    background:#0f172a;border-radius:10px;padding:10px 12px;min-width:200px;max-width:300px;
    box-shadow:0 12px 34px -8px rgba(0,0,0,.45);text-align:left;white-space:nowrap}
  .pop::before{content:"";position:absolute;bottom:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-bottom-color:#0f172a}
  .dcell:hover .pop{display:block}
  .pop-h{font-size:10px;color:#cbd5e1;text-transform:uppercase;letter-spacing:.05em;margin-bottom:7px;font-weight:600}
  .pop-u{font-size:12.5px;color:#fff;padding:4px 0;border-top:1px solid rgba(255,255,255,.09)}
  .pop-u:first-of-type{border-top:none}
  .pop-u b{font-weight:600}
  .pop-u span{display:block;font-size:10.5px;color:#94a3b8;font-weight:400}
  .stable{width:100%;border-collapse:collapse}
  .stable th{font-size:10.5px;text-transform:uppercase;letter-spacing:.03em;color:var(--text-3);text-align:left;padding:9px 10px;border-bottom:1px solid var(--border)}
  .stable td{font-size:12.5px;color:var(--text-2);padding:9px 10px;border-bottom:1px solid var(--border-2)}
  .stable td.r,.stable th.r{text-align:right}
  .stable td.usr b{color:var(--text-1);font-weight:600}
  .stable td.usr .em{display:block;font-size:11px;color:var(--text-3)}
  .stable tr:last-child td{border-bottom:none}

  /* funnel */
  .funnel{display:flex;align-items:stretch;gap:14px;background:var(--card);border:1px solid var(--border);
    border-radius:var(--r);padding:24px;margin-bottom:14px;flex-wrap:wrap;box-shadow:var(--shadow-sm)}
  .fstep{flex:1;min-width:150px;display:flex;flex-direction:column;justify-content:flex-end;gap:9px}
  .flabel{font-size:12px;font-weight:600;letter-spacing:.03em;text-transform:uppercase;color:var(--text-3)}
  .fnum{font-size:34px;font-weight:800;letter-spacing:-.02em}
  .fstep.accent .fnum{color:var(--accent)}
  .fbar{height:8px;border-radius:var(--r-pill);background:#eef0f3;overflow:hidden}
  .fbar i{display:block;height:100%;border-radius:var(--r-pill);background:linear-gradient(90deg,var(--accent-2),var(--accent))}
  .fsub{font-size:11.5px;color:var(--text-3);line-height:1.45}
  .fsub span{color:var(--accent);font-family:ui-monospace,Menlo,monospace;font-size:10.5px}
  .farrow{display:flex;align-items:center;color:#cbd2dc;font-size:20px}
  @media(max-width:720px){.farrow{display:none}}
  .fconv{min-width:180px;background:var(--accent-soft);border:1px solid #dcdcfb;border-radius:var(--r-sm);
    padding:18px;display:flex;flex-direction:column;justify-content:center;gap:3px}
  .fconv-num{font-size:42px;font-weight:800;letter-spacing:-.03em;color:var(--accent)}
  .fconv-lbl{font-size:12px;font-weight:700;color:var(--accent);letter-spacing:.03em;text-transform:uppercase}
  .fconv-sub{font-size:11.5px;color:var(--text-2);margin-top:7px;line-height:1.5}
  .fconv-sub .warn{color:var(--warn)}
  .note{font-size:12px;color:var(--text-3);margin:0 0 34px;padding-left:2px;line-height:1.6}
  .note b{color:var(--text-2)}

  /* step drop-off */
  .steps{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:22px 24px;margin-bottom:34px;box-shadow:var(--shadow-sm)}
  .srow{display:flex;align-items:center;gap:12px;padding:3px 0}
  .slabel{width:160px;font-size:12.5px;color:var(--text-2);flex-shrink:0}
  .strack{flex:1;height:26px;background:#f1f3f6;border-radius:7px;overflow:hidden}
  .sfill{height:100%;background:linear-gradient(90deg,var(--accent-2),var(--accent));border-radius:7px;
    display:flex;align-items:center;justify-content:flex-end;padding-right:9px;color:#fff;font-size:11px;font-weight:600;min-width:34px}
  .sfill.warn{background:linear-gradient(90deg,#f6c343,var(--warn))}
  .sfill.bad{background:linear-gradient(90deg,#f0795f,var(--danger))}
  .sdrop{width:58px;font-size:11px;font-weight:700;text-align:right;flex-shrink:0}
  .sdrop.big{color:var(--danger)}
  .sdrop.mid{color:var(--warn)}
  @media(max-width:560px){.slabel{width:110px;font-size:11px}.sdrop{width:44px}}

  /* palanca grid */
  .grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-bottom:34px}
  @media(max-width:980px){.grid{grid-template-columns:repeat(2,1fr)}}
  @media(max-width:520px){.grid{grid-template-columns:1fr}}
  .card{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:20px;
    display:flex;flex-direction:column;gap:11px;box-shadow:var(--shadow-sm);transition:.18s}
  .card:hover{box-shadow:var(--shadow);transform:translateY(-2px)}
  .card.muted{opacity:.65}
  .card .n{display:flex;justify-content:space-between;align-items:center}
  .chip{font-size:10.5px;font-weight:600;letter-spacing:.03em;text-transform:uppercase;color:var(--text-3);
    background:#f1f3f6;padding:4px 10px;border-radius:var(--r-pill)}
  .idx{width:27px;height:27px;border-radius:8px;background:var(--accent-soft);color:var(--accent);
    font-size:13px;font-weight:800;display:flex;align-items:center;justify-content:center}
  .card h3{font-size:15.5px;font-weight:700}
  .vals{display:flex;align-items:baseline;gap:9px;margin-top:2px}
  .vnow{font-size:30px;font-weight:800;letter-spacing:-.02em}
  .vnow.bad{color:var(--danger)}
  .vnow.warn{color:var(--warn)}
  .vtar{font-size:12.5px;color:var(--text-3)}
  .vtar b{color:var(--text-2)}
  .cardsub{font-size:11.5px;color:var(--text-3);margin-top:-3px}
  .cardsub b{color:var(--text-2);font-weight:600}
  .lever{font-size:12px;color:var(--text-3);border-top:1px solid var(--border);padding-top:11px;margin-top:2px}
  .lever b{color:var(--text-2);font-weight:600}

  /* tree */
  .tree-wrap{background:var(--card);border:1px solid var(--border);border-radius:var(--r);padding:28px 22px;box-shadow:var(--shadow-sm)}
  .tree{display:flex;flex-direction:column;align-items:center}
  .node-star{background:var(--accent);color:#fff;padding:13px 24px;border-radius:var(--r-pill);
    font-weight:700;font-size:15px;box-shadow:0 6px 20px -6px rgba(79,70,229,.5)}
  .node-star span{color:#c7c5f7}
  .connector{width:2px;height:26px;background:var(--border-2)}
  .branch{display:flex;justify-content:center;gap:16px;width:100%;flex-wrap:wrap}
  .leaf{flex:1;min-width:160px;max-width:240px;text-align:center}
  .leaf .h{width:2px;height:18px;background:var(--border-2);margin:0 auto}
  .leaf .box{background:var(--card-2);border:1px solid var(--border);border-radius:var(--r-sm);padding:13px 11px}
  .leaf .box .t{font-size:13px;font-weight:700;margin-bottom:3px}
  .leaf .box .d{font-size:11px;color:var(--text-3)}
  .leaf .box .lv{font-size:10.5px;color:var(--accent);margin-top:7px;font-weight:600}
</style>
</head>
<body>
<div class="wrap">

  <div class="top">
    <div>
      <div class="eyebrow">El Metodo · Automática</div>
      <h1>North Star Dashboard</h1>
    </div>
    <div class="updated">@@UPDATED@@</div>
  </div>

  <div class="meta">Meta-norte: <b>personas viviendo una vida deportiva constante</b> — romper el ciclo inicio → abandono → culpa.</div>

  <!-- NORTH STAR HERO -->
  <div class="hero">
    <div class="hero-grid">
      <div>
        <div class="star-label">⭐ NORTH STAR METRIC</div>
        <div class="star-name">Usuarios consistentes</div>
        <div class="star-def">usuarios que completan +2 sesiones reales de entreno en 7 días</div>
        <div class="star-num">
          <span class="big">@@NS_BIG@@</span>
          <span class="trend @@NS_TREND_CLS@@">@@NS_TREND@@</span>
        </div>
        <div class="star-foot">Meta trimestre: <b style="color:var(--accent)">@@GOAL@@</b> · progreso @@NS_PROG@@</div>
        <div class="progress" style="margin-top:12px;max-width:330px"><i style="width:@@NS_PROG_W@@"></i></div>
      </div>
      <div>
        <div class="spark">
@@SPARK_BARS@@
        </div>
        <div class="spark-cap">@@SPARK_CAP@@</div>
      </div>
    </div>
  </div>

  <!-- ENTRENOS · SEMANA x DIA -->
  <div class="sec">Entrenos — usuarios que completaron ≥1 sesión real, por día</div>
  <div class="panel pop-ok">
    <table class="dgrid">
@@GRID_ROWS@@
    </table>
    <div class="panel-note">Cada celda = nº de usuarios distintos que completaron ≥1 sesión <b>real</b> (≥5 min, o ≥1 ejercicio si falta la duración) ese día — <b>pasa el ratón por encima para ver quién entrenó</b> (nombre y email). <b>ses.</b> = sesiones reales de la semana · <b>min</b> = mediana de minutos por sesión. Se eliminan los disparos duplicados del evento.</div>
  </div>

  <!-- ENTRENOS · DETALLE -->
  <div class="sec">Últimas sesiones reales — quién, qué programa, qué sesión, cuántos minutos</div>
  <div class="panel">
    <table class="stable">
@@DETAIL_ROWS@@
    </table>
  </div>

  <!-- EMBUDO NUEVO -->
  <div class="sec">Negocio — embudo nuevo: cuestionario → registro → pago</div>
  <div class="funnel">
    <div class="fstep">
      <div class="flabel">Inició</div>
      <div class="fnum">@@F_INICIO@@</div>
      <div class="fbar"><i style="width:100%"></i></div>
      <div class="fsub">abren el onboarding</div>
    </div>
    <div class="farrow">→</div>
    <div class="fstep">
      <div class="flabel">Completó quiz</div>
      <div class="fnum">@@F_QUIZ@@</div>
      <div class="fbar"><i style="width:@@FW_QUIZ@@"></i></div>
      <div class="fsub">@@FC_QUIZ@@ · recibió programa</div>
    </div>
    <div class="farrow">→</div>
    <div class="fstep">
      <div class="flabel">Registro</div>
      <div class="fnum">@@F_REG@@</div>
      <div class="fbar"><i style="width:@@FW_REG@@"></i></div>
      <div class="fsub">@@FC_REG@@ · crean cuenta</div>
    </div>
    <div class="farrow">→</div>
    <div class="fstep accent">
      <div class="flabel">Pago</div>
      <div class="fnum">@@F_PAGO@@</div>
      <div class="fbar"><i style="width:@@FW_PAGO@@"></i></div>
      <div class="fsub">@@FC_PAGO@@ · pagó / trial</div>
    </div>
    <div class="fconv">
      <div class="fconv-num">@@FCONV@@</div>
      <div class="fconv-lbl">inicio&nbsp;→&nbsp;registro</div>
      <div class="fconv-sub">registro → pago: <b style="color:var(--accent)">@@FC_REG2PAY@@</b><br>inicio → pago: @@FC_PAGO@@</div>
    </div>
  </div>

  <!-- DROP-OFF POR PASO -->
  <div class="sec">Dónde se cae la gente — los @@N_STEPS@@ pasos del onboarding</div>
  <div class="steps">
@@STEP_ROWS@@
  </div>

  <!-- PALANCAS -->
  <div class="sec">Las 3 palancas que la mueven</div>
  <div class="grid">

    <div class="card">
      <div class="n"><div class="idx">1</div><div class="chip">Entrada</div></div>
      <h3>Activación temprana</h3>
      <div class="vals"><span class="vnow @@P1_CLS@@">@@P1_VAL@@</span><span class="vtar">meta <b>@@META_ACT@@</b></span></div>
      <div class="cardsub">@@P1_SUB@@</div>
      <div class="progress warn"><i style="width:@@P1_W@@"></i></div>
    </div>

    <div class="card">
      <div class="n"><div class="idx">2</div><div class="chip">Vuelta diaria</div></div>
      <h3>Enganche social</h3>
      <div class="vals"><span class="vnow @@P2_CLS@@">@@P2_VAL@@</span><span class="vtar">meta <b>@@META_ENG@@</b></span></div>
      <div class="cardsub">@@P2_SUB@@</div>
      <div class="progress warn"><i style="width:@@P2_W@@"></i></div>
    </div>

    <div class="card">
      <div class="n"><div class="idx">3</div><div class="chip">Skin in the game</div></div>
      <h3>Compromiso por pago</h3>
      <div class="vals"><span class="vnow @@P3_CLS@@">@@P3_VAL@@</span><span class="vtar">meta <b>@@META_COM@@</b></span></div>
      <div class="cardsub">@@P3_SUB@@</div>
      <div class="progress warn"><i style="width:@@P3_W@@"></i></div>
    </div>

  </div>

  <!-- TREE -->
  <div class="sec">El árbol — cómo se conecta todo</div>
  <div class="tree-wrap">
    <div class="tree">
      <div class="node-star">⭐ Usuarios consistentes <span>(≥2 entrenos / 7 días)</span></div>
      <div class="connector"></div>
      <div class="branch">
        <div class="leaf"><div class="h"></div><div class="box"><div class="t">1 · Activación temprana</div><div class="d">1er entreno en 3 días</div><div class="lv">Onboarding · efecto IKEA</div></div></div>
        <div class="leaf"><div class="h"></div><div class="box"><div class="t">2 · Enganche social</div><div class="d">ranking ≥3 días/sem</div><div class="lv">Ligas · XP unificado</div></div></div>
        <div class="leaf"><div class="h"></div><div class="box"><div class="t">3 · Compromiso por pago</div><div class="d">trial → paid</div><div class="lv">Paywall compromiso</div></div></div>
      </div>
    </div>
  </div>

</div>
</body>
</html>
"""

if __name__ == "__main__":
    main()
