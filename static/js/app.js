// Utilidades comunes + lógica por página (document.body.dataset.page)
const $ = (s) => document.querySelector(s);
const MESES = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"];
const DIAS = ["Domingo","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"];
const params = new URLSearchParams(location.search);
const EMAIL_RE = /^[\w.+-]+@[\w-]+(\.[\w-]+)+$/;
const USER = JSON.parse(sessionStorage.getItem("axis_user") || "null");
function eye() {   // botón "ojito" para ver/ocultar la contraseña
  document.querySelectorAll(".eye").forEach((b) => b.onclick = () => {
    const i = b.previousElementSibling, ver = i.type === "password";
    i.type = ver ? "text" : "password"; b.textContent = ver ? "🙈" : "👁";
    b.setAttribute("aria-pressed", ver); b.setAttribute("aria-label", ver ? "Ocultar contraseña" : "Mostrar contraseña");
  });
}

// Si la página no se sirve desde FastAPI (file://, Live Server), apunta al backend local
const BASE = location.port === "8000" ? "" : "http://127.0.0.1:8000";

async function api(ruta, opciones = {}) {
  let r;
  try {
    r = await fetch(BASE + "/api" + ruta, { headers: { "Content-Type": "application/json", ...(USER ? { "X-User": USER.email } : {}) }, ...opciones });
  } catch {
    throw new Error("No se pudo conectar con el servidor. ¿Está corriendo uvicorn main:app --reload?");
  }
  const datos = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(typeof datos.detail === "string" ? datos.detail : "Revisá los datos ingresados");
  return datos;
}
const d = (iso) => new Date(iso + "T00:00:00");
const iso = (f) => `${f.getFullYear()}-${String(f.getMonth() + 1).padStart(2, "0")}-${String(f.getDate()).padStart(2, "0")}`;
const corta = (i) => { const f = d(i); return `${DIAS[f.getDay()]} ${f.getDate()} de ${MESES[f.getMonth()]}`; };
const larga = (i) => `${corta(i)} de ${d(i).getFullYear()}`;
function toast(msg) {
  const t = document.createElement("div"); t.id = "toast"; t.setAttribute("role", "status"); t.textContent = msg;
  document.body.append(t); setTimeout(() => t.remove(), 2800);
}
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

const paginas = {
  async login() {
    eye();
    const recordado = localStorage.getItem("axis_email");
    if (recordado) { $("#email").value = recordado; $("#rec").checked = true; }
    if (params.get("registrado")) {
      $("#msg").textContent = "¡Cuenta creada! Ingresá con tu correo y contraseña.";
      $("#email").value = params.get("email") || "";
    }
    $("#form").addEventListener("submit", async (e) => {
      e.preventDefault(); $("#err").textContent = "";
      const email = $("#email").value.trim(), clave = $("#pass").value;
      if (!EMAIL_RE.test(email)) { $("#err").textContent = "Ingresá un correo válido, por ejemplo nombre@dominio.com"; return; }
      if (clave.length < 8) { $("#err").textContent = "La contraseña debe tener al menos 8 caracteres"; return; }
      try {
        const u = await api("/login", { method: "POST", body: JSON.stringify({ email, password: clave }) });
        sessionStorage.setItem("axis_user", JSON.stringify(u));
        if ($("#rec").checked) localStorage.setItem("axis_email", email); else localStorage.removeItem("axis_email");
        location.href = "panel.html";
      } catch (er) { $("#err").textContent = er.message; }
    });
  },

  async registro() {
    eye();
    $("#nac").max = iso(new Date());
    $("#form").addEventListener("submit", async (e) => {
      e.preventDefault(); $("#err").textContent = "";
      const f = new FormData($("#form")), email = $("#email").value.trim(), clave = $("#pass").value;
      if (!EMAIL_RE.test(email)) { $("#err").textContent = "Ingresá un correo válido, por ejemplo nombre@dominio.com"; return; }
      if (clave !== $("#pass2").value) { $("#err").textContent = "Las contraseñas no coinciden"; return; }
      try {
        await api("/registro", { method: "POST", body: JSON.stringify({
          nombre: f.get("nombre"), apellido: f.get("apellido"), nacimiento: f.get("nacimiento"), genero: f.get("genero"),
          email, telefono: f.get("telefono"), direccion: f.get("direccion") || "", clave }) });
        location.href = "index.html?registrado=1&email=" + encodeURIComponent(email);
      } catch (er) { $("#err").textContent = er.message; }
    });
  },

  async panel() {
    const [p, r, t] = await Promise.all([api("/paciente"), api("/resumen"), api("/turnos?vista=proximos")]);
    $("#nombre").textContent = `${p.nombre} ${p.apellido}`;
    $("#n-prox").textContent = r.proximos; $("#n-real").textContent = r.realizados; $("#n-rec").textContent = r.recordatorios;
    $("#lista").innerHTML = t.length ? t.map((x) => `<div class="row"><div><b>${esc(x.profesional)}</b>
      <small>${esc(x.especialidad)} · ${corta(x.fecha)} · ${x.hora} hs</small></div>
      <span class="badge ${x.estado}">${x.estado}</span></div>`).join("")
      : `<p class="empty">No tenés turnos próximos. <a href="nuevo-turno.html">Agendá uno</a>.</p>`;
  },

  async nuevo() {
    const S = { esp: null, prof: null, fecha: null, hora: null, mes: new Date() };
    S.mes.setDate(1);
    const reprog = params.get("reprogramar");
    const hoy = iso(new Date());
    const marcar = (n) => document.querySelectorAll(".step").forEach((el, i) => {
      el.classList.toggle("on", i + 1 === n); el.classList.toggle("done", i + 1 < n);
    });

    async function elegirEsp(esp) {
      S.esp = esp; S.prof = null; S.fecha = null; S.hora = null;
      $("#esp").value = esp;
      $("#s-fecha").classList.add("hidden"); $("#cont").setAttribute("aria-disabled", "true");
      if (!esp) { $("#s-prof").classList.add("hidden"); marcar(1); return; }
      const profs = await api("/profesionales?especialidad=" + encodeURIComponent(esp));
      $("#prof").innerHTML = '<option value="">Elegí un profesional</option>' +
        profs.map((p) => `<option value="${p.id}">${esc(p.nombre)} — ${esc(p.centro)}</option>`).join("");
      $("#s-prof").classList.remove("hidden"); marcar(2);
    }
    function elegirProf(id) {
      S.prof = id; S.fecha = null; S.hora = null; $("#prof").value = id || "";
      $("#cont").setAttribute("aria-disabled", "true");
      if (!id) { $("#s-fecha").classList.add("hidden"); marcar(2); return; }
      $("#s-fecha").classList.remove("hidden"); $("#slots").innerHTML = ""; $("#cont").setAttribute("aria-disabled", "true");
      $("#h-tit").textContent = "Elegí una fecha para ver los horarios"; marcar(3); calendario();
    }
    function calendario() {
      const y = S.mes.getFullYear(), m = S.mes.getMonth();
      $("#mes").textContent = `${MESES[m][0].toUpperCase()}${MESES[m].slice(1)} ${y}`;
      const offset = (new Date(y, m, 1).getDay() + 6) % 7, total = new Date(y, m + 1, 0).getDate();
      let h = ["Lu","Ma","Mi","Ju","Vi","Sá","Do"].map((x) => `<b>${x}</b>`).join("") + "<span></span>".repeat(offset);
      for (let n = 1; n <= total; n++) {
        const f = new Date(y, m, n), i = iso(f), off = i < hoy || f.getDay() % 6 === 0;
        h += `<button class="day ${i === S.fecha ? "sel" : ""}" data-f="${i}" ${off ? "disabled" : ""}>${n}</button>`;
      }
      $("#dias").innerHTML = h;
      document.querySelectorAll(".day").forEach((b) => b.onclick = () => elegirFecha(b.dataset.f));
    }
    async function elegirFecha(f) {
      S.fecha = f; S.hora = null; calendario();
      $("#cont").setAttribute("aria-disabled", "true");
      const hs = await api(`/horarios?profesional_id=${S.prof}&fecha=${f}` + (reprog ? `&ignorar_id=${reprog}` : ""));
      $("#h-tit").textContent = `Horarios disponibles — ${corta(f)}`;
      $("#slots").innerHTML = hs.length ? hs.map((x) => `<button class="slot" data-h="${x}">${x}</button>`).join("")
        : `<p class="empty">No hay horarios libres ese día. Probá con otra fecha.</p>`;
      document.querySelectorAll(".slot").forEach((b) => b.onclick = () => {
        S.hora = b.dataset.h;
        document.querySelectorAll(".slot").forEach((x) => x.classList.toggle("sel", x === b));
        $("#cont").href = `confirmar.html?prof=${S.prof}&fecha=${S.fecha}&hora=${S.hora}` + (reprog ? `&reprogramar=${reprog}` : "");
        $("#cont").removeAttribute("aria-disabled");
      });
    }
    $("#prev").onclick = () => { S.mes.setMonth(S.mes.getMonth() - 1); calendario(); };
    $("#next").onclick = () => { S.mes.setMonth(S.mes.getMonth() + 1); calendario(); };

    const esps = await api("/especialidades");
    $("#esp").innerHTML = '<option value="">Elegí una especialidad</option>' + esps.map((e) => `<option>${esc(e)}</option>`).join("");
    $("#esp").onchange = () => elegirEsp($("#esp").value);
    $("#prof").onchange = () => elegirProf(+$("#prof").value);
    marcar(1);
    if (reprog) {                       // reprogramar: parte del profesional ya elegido
      const t = await api("/turnos/" + reprog);
      $("h1").lastChild.textContent = " Reprogramar turno";
      await elegirEsp(t.especialidad); elegirProf(t.profesional_id);
    }
  },

  async confirmar() {
    const reprog = params.get("reprogramar"), id = +params.get("prof"), fecha = params.get("fecha"), hora = params.get("hora");
    const p = (await api("/profesionales")).find((x) => x.id === id);
    if (!p || !fecha || !hora) { location.href = "nuevo-turno.html"; return; }
    $("#r-esp").textContent = p.especialidad; $("#r-prof").textContent = p.nombre;
    $("#r-fecha").textContent = larga(fecha); $("#r-hora").textContent = hora + " hs"; $("#r-centro").textContent = p.centro;
    $("#ubic").href = "https://www.google.com/maps/search/" + encodeURIComponent(p.centro);
    $("#ok").onclick = async () => {
      try {
        if (reprog) await api(`/turnos/${reprog}/reprogramar`, { method: "PUT", body: JSON.stringify({ fecha, hora }) });
        else await api("/turnos", { method: "POST", body: JSON.stringify({ profesional_id: id, fecha, hora }) });
        location.href = "mis-turnos.html?ok=1";
      } catch (e) { toast(e.message); }
    };
  },

  async turnos() {
    let vista = "proximos";
    if (params.get("ok")) toast("¡Turno agendado! Te enviaremos los recordatorios.");
    async function cargar() {
      document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("on", t.dataset.v === vista));
      const lista = await api("/turnos?vista=" + vista);
      $("#lista").innerHTML = lista.length ? lista.map((t) => {
        const rec = new Date(d(t.fecha)); rec.setDate(rec.getDate() - 1);
        const aviso = vista !== "proximos" ? "" : t.estado === "Confirmado"
          ? `<div class="note ok">🔔 Recordatorio programado para el ${DIAS[rec.getDay()].toLowerCase()} ${rec.getDate()} a las 10:30 hs por WhatsApp</div>`
          : `<div class="note warn">⚠ Confirmá tu asistencia antes del ${corta(iso(rec)).toLowerCase()} para mantener el turno</div>`;
        const acc = vista !== "proximos" ? "" : `<div class="btns">${t.estado === "Pendiente" ? `<button class="btn primary" data-a="confirmar" data-id="${t.id}">Confirmar asistencia</button>` : ""}
          <a class="btn" href="nuevo-turno.html?reprogramar=${t.id}">Reprogramar</a>
          ${t.estado === "Confirmado" ? `<button class="btn danger" data-a="cancelar" data-id="${t.id}">Cancelar turno</button>` : ""}</div>`;
        return `<article class="tcard"><div class="head"><div><h3>${esc(t.profesional)}</h3><small>${esc(t.especialidad)} - ${esc(t.centro)}</small></div>
          <span class="badge ${t.estado}">${t.estado}</span></div>
          <div class="meta"><span>📅 ${larga(t.fecha)}</span><span>🕒 ${t.hora} hs</span></div>${aviso}${acc}</article>`;
      }).join("") : `<p class="empty">No hay turnos en esta sección.</p>`;
      document.querySelectorAll("[data-a]").forEach((b) => b.onclick = async () => {
        if (b.dataset.a === "cancelar" && !confirm("¿Querés cancelar este turno?")) return;
        await api(`/turnos/${b.dataset.id}/${b.dataset.a}`, { method: "PUT" });
        toast(b.dataset.a === "cancelar" ? "Turno cancelado" : "Asistencia confirmada"); cargar();
      });
    }
    document.querySelectorAll(".tab").forEach((t) => t.onclick = () => { vista = t.dataset.v; cargar(); });
    cargar();
  },

  async perfil() {
    const p = await api("/paciente");
    $("#datos").innerHTML = Object.entries({ Nombre: `${p.nombre} ${p.apellido}`, "Correo electrónico": p.email, Teléfono: p.telefono,
      "Fecha de nacimiento": p.nacimiento ? larga(p.nacimiento).split(" ").slice(1).join(" ") : "—", Género: p.genero, Dirección: p.direccion || "—" })
      .map(([k, v]) => `<div class="row"><span>${k}</span><b>${esc(v)}</b></div>`).join("");
  },
};
const pag = document.body.dataset.page;
if (!["login", "registro"].includes(pag) && !USER) location.replace("index.html");   // sin sesión → login
else {
  if (USER && $("#av")) {
    $("#av").textContent = (USER.nombre[0] + (USER.apellido[0] || "")).toUpperCase();
    $("#un").textContent = USER.nombre;
    $("#salir").onclick = () => sessionStorage.removeItem("axis_user");
  }
  paginas[pag]?.().catch((e) => toast(e.message));
}
