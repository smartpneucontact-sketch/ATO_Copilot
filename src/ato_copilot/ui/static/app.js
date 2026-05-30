(() => {
  const $ = (id) => document.getElementById(id);
  const escape = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  document.querySelectorAll("[data-scroll]").forEach((a) => {
    a.addEventListener("click", (e) => {
      const href = a.getAttribute("href");
      if (!href || !href.startsWith("#")) return;
      const el = document.querySelector(href);
      if (!el) return;
      e.preventDefault();
      el.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  fetch("/healthz").then((r) => r.json()).then((h) => {
    const isLive = !h.use_mock_llm;
    const pill = $("mode-pill");
    pill.classList.add(isLive ? "live" : "mock");
    $("mode-text").textContent = isLive ? `LIVE · ${h.model}` : `MOCK · ${h.model}`;
    $("footer-mode").textContent = isLive ? `LIVE (${h.model})` : `MOCK (${h.model})`;
    $("stat-corpus").textContent = h.corpus_chunks ?? "—";
    $("stat-model").textContent = h.model;
  }).catch(() => {
    $("mode-pill").classList.add("mock");
    $("mode-text").textContent = "offline";
  });

  let samples = [];
  fetch("/api/samples/requests").then((r) => r.json()).then((data) => {
    samples = data;
    const sel = $("req-sample");
    data.forEach((s, i) => {
      const opt = document.createElement("option");
      opt.value = i;
      opt.textContent = `${s.request_id} — ${(s.business_unit || "").slice(0, 28)}`;
      sel.appendChild(opt);
    });
    loadSample(0);
  });

  const loadSample = (i) => {
    const s = samples[i];
    if (!s) return;
    $("req-id").value = s.request_id || "";
    $("req-date").value = s.date || "";
    $("req-submitter").value = s.submitted_by || "";
    $("req-bu").value = s.business_unit || "";
    $("req-description").value = s.description || "";
  };
  $("req-sample").addEventListener("change", (e) => loadSample(+e.target.value));

  document.querySelectorAll(".btn-primary").forEach((b) => {
    const t = b.querySelector(".btn-text");
    if (t && !b.dataset.label) b.dataset.label = t.textContent;
  });

  $("req-submit").addEventListener("click", async () => {
    const btn = $("req-submit");
    const status = $("req-status");
    const empty = $("req-empty");
    const result = $("req-result");

    const payload = {
      request_id: $("req-id").value.trim() || "NTAP-DEMO",
      date: $("req-date").value.trim(),
      submitted_by: $("req-submitter").value.trim(),
      business_unit: $("req-bu").value.trim(),
      description: $("req-description").value.trim(),
    };

    setSubmitting(btn, true);
    showStatus(status, "running", "Retrieving governance context and drafting ATO package…");
    empty.hidden = true;
    result.hidden = false;
    result.innerHTML = renderRunningSkeleton();
    const t0 = performance.now();

    try {
      const resp = await fetch("/agents/ato/triage", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) throw new Error(await formatError(resp));
      const data = await resp.json();
      const wall = Math.round(performance.now() - t0);
      result.innerHTML = renderResult(data, wall);
      showStatus(status, "ok", `Done — run_id ${data.run_id}`);
    } catch (e) {
      result.innerHTML = "";
      empty.hidden = false;
      showStatus(status, "error", e.message);
    } finally {
      setSubmitting(btn, false);
    }
  });

  const setSubmitting = (btn, on) => {
    btn.disabled = on;
    btn.querySelector(".btn-text").textContent = on ? "Running…" : btn.dataset.label;
    btn.querySelector(".btn-spinner").hidden = !on;
  };
  const showStatus = (el, kind, msg) => {
    if (!msg) { el.hidden = true; el.className = "status"; return; }
    el.hidden = false;
    el.className = `status ${kind}`;
    el.textContent = msg;
  };
  async function formatError(resp) {
    let msg = `HTTP ${resp.status}`;
    try {
      const body = await resp.json();
      if (body && body.detail) {
        if (typeof body.detail === "string") msg = `${msg}: ${body.detail}`;
        else msg = `${body.detail.error || "Error"}: ${body.detail.message || JSON.stringify(body.detail)}`;
      }
    } catch (_) {}
    return msg;
  }

  const renderRunningSkeleton = () => `
    <div class="telemetry-strip">
      ${["Run","Steps","Tokens","Cost"].map((l) => `
        <div class="telem-cell"><div class="telem-label">${l}</div><div class="telem-value">…</div></div>
      `).join("")}
    </div>
    <div class="empty-state" style="padding:50px 20px">
      <p class="muted">Agent is thinking — typically 8–15 seconds with tool calls.</p>
    </div>
  `;

  const telemetryStrip = (data, wallMs) => {
    const cost = (data.cost_usd ?? 0).toFixed(4);
    return `
      <div class="telemetry-strip">
        <div class="telem-cell"><div class="telem-label">Steps</div><div class="telem-value">${data.steps ?? 0}</div></div>
        <div class="telem-cell"><div class="telem-label">Tokens</div><div class="telem-value">${(data.input_tokens || 0).toLocaleString()} <span class="muted" style="font-size:11px">in</span> · ${(data.output_tokens || 0).toLocaleString()} <span class="muted" style="font-size:11px">out</span></div></div>
        <div class="telem-cell"><div class="telem-label">Cost</div><div class="telem-value">$${cost}</div></div>
        <div class="telem-cell"><div class="telem-label">Wall time</div><div class="telem-value">${(wallMs / 1000).toFixed(1)}s</div></div>
      </div>
    `;
  };

  const renderResult = (data, wallMs) => {
    const p = data.parsed || {};
    const parts = [telemetryStrip(data, wallMs)];

    if (p.request_summary) {
      parts.push(`
        <div class="result-section">
          <h4 class="result-section-title">Normalized request summary</h4>
          <div class="summary-card">${escape(p.request_summary)}</div>
        </div>
      `);
    } else if (data.final_text) {
      parts.push(`<div class="result-section"><h4 class="result-section-title">Raw output</h4><div class="summary-card">${escape(data.final_text)}</div></div>`);
    }

    // Decision + risk + ARB badges
    const badges = [];
    if (p.recommended_decision) {
      const cls = String(p.recommended_decision).toLowerCase().replace(/[^a-z]+/g, "-");
      badges.push(`<span class="badge decision-${cls}"><span class="b-label">decision</span><span class="b-value">${escape(p.recommended_decision)}</span></span>`);
    }
    if (p.risk_classification && p.risk_classification.band) {
      badges.push(`<span class="badge risk-${p.risk_classification.band}"><span class="b-label">risk</span><span class="b-value">${escape(p.risk_classification.band)}</span></span>`);
    }
    if (p.estimated_days_to_decision !== undefined) {
      badges.push(`<span class="badge"><span class="b-label">cycle time</span><span class="b-value">${escape(p.estimated_days_to_decision)} d</span></span>`);
    }
    if (p.needs_arb_review !== undefined) {
      const yes = !!p.needs_arb_review;
      badges.push(`<span class="badge flag-${yes ? "yes" : "no"}"><span class="b-label">ARB review</span><span class="b-value">${yes ? "required" : "not required"}</span></span>`);
    }
    if (badges.length) {
      parts.push(`<div class="result-section"><div class="badges">${badges.join("")}</div></div>`);
    }

    // ATL status
    if (p.atl_status && typeof p.atl_status === "object") {
      const a = p.atl_status;
      const cls = String(a.status || "").toLowerCase().replace(/[^a-z_]+/g, "_");
      parts.push(`
        <div class="result-section">
          <h4 class="result-section-title">Approved Technology List check</h4>
          <div class="atl-card">
            <span class="atl-status ${cls}">${escape(a.status || "—")}</span>
            <div class="atl-body">
              ${a.approved_entry ? `<div class="atl-entry">${escape(a.approved_entry)}</div>` : ""}
              ${a.note ? `<div class="atl-note">${escape(a.note)}</div>` : ""}
              ${a.source ? `<div class="atl-source">${escape(a.source)}</div>` : ""}
            </div>
          </div>
        </div>
      `);
    }

    // Control mapping
    if (Array.isArray(p.control_mapping) && p.control_mapping.length) {
      const items = p.control_mapping.map((c) => `
        <div class="control-row">
          <span class="control-name">${escape(c.control || "")}</span>
          <span class="control-applicability ${escape((c.applicability || "").toLowerCase().split(" ")[0])}">${escape((c.applicability || "—").split(" ")[0])}</span>
          ${c.source ? `<span class="control-source">${escape(c.source)}</span>` : ""}
        </div>
      `).join("");
      parts.push(`<div class="result-section"><h4 class="result-section-title">Control mapping · ${p.control_mapping.length}</h4>${items}</div>`);
    }

    // Architecture review
    if (p.architecture_review && typeof p.architecture_review === "object") {
      const a = p.architecture_review;
      const fits = a.fits_reference_architecture ? "fits reference architecture" : "does not fit reference architecture";
      parts.push(`
        <div class="result-section">
          <h4 class="result-section-title">Architecture review</h4>
          <div class="summary-card">
            <strong>${escape(a.pattern || "no clean match")}</strong> — ${escape(fits)}
            ${Array.isArray(a.issues) && a.issues.length ? `<ul class="list-tight" style="margin-top:8px">${a.issues.map((s) => `<li>${escape(s)}</li>`).join("")}</ul>` : ""}
          </div>
        </div>
      `);
    }

    if (Array.isArray(p.open_items) && p.open_items.length) {
      parts.push(`<div class="result-section"><h4 class="result-section-title">Open items before decision</h4><ul class="list-tight">${p.open_items.map((s) => `<li>${escape(s)}</li>`).join("")}</ul></div>`);
    }

    if (p.rationale) {
      parts.push(`<div class="result-section"><h4 class="result-section-title">Reviewer rationale</h4><div class="rationale">${escape(p.rationale)}</div></div>`);
    }

    if (data.tool_invocations && data.tool_invocations.length) {
      parts.push(renderTimeline(data.tool_invocations));
    }

    return parts.join("");
  };

  const renderTimeline = (invocations) => {
    const steps = invocations.map((inv, i) => `
      <div class="tool-step">
        <div class="tool-dot">${i + 1}</div>
        <details class="tool-card" ${i === 0 ? "open" : ""}>
          <summary>
            <span class="tool-name">${escape(inv.name)}</span>
            <span class="tool-args">${escape(formatToolArgs(inv.input))}</span>
          </summary>
          <div class="tool-body">${renderToolResult(inv)}</div>
        </details>
      </div>
    `).join("");
    return `
      <div class="result-section">
        <h4 class="result-section-title">Agent reasoning · ${invocations.length} tool calls</h4>
        <div class="timeline">${steps}</div>
      </div>
    `;
  };

  const formatToolArgs = (obj) => {
    if (!obj || typeof obj !== "object") return "";
    return Object.entries(obj).map(([k, v]) => {
      const sv = typeof v === "string" && v.length > 50 ? v.slice(0, 50) + "…" : JSON.stringify(v);
      return `${k}=${sv}`;
    }).join(", ");
  };

  const renderToolResult = (inv) => {
    const r = inv.result;
    if (r && Array.isArray(r.results)) {
      const items = r.results.slice(0, 8).map((x) => `
        <li>
          <span class="ret-id">${escape(x.source_type)}:${escape(x.source_id)}${x.section ? " · " + escape(x.section) : ""}</span>
          <span class="ret-score">${x.score}</span>
        </li>
      `).join("");
      return `<div class="muted" style="margin-top:10px;font-size:12px">${r.count} chunks returned</div><ul class="retrieved-list">${items}</ul>`;
    }
    return `<pre>${escape(JSON.stringify(r, null, 2))}</pre>`;
  };
})();
