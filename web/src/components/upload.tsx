"use client";
import { useState } from "react";
import { API, api, Manifest, Row, str } from "@/lib/data";
import { Icon, PageHead } from "./shell";
import { ReadoutBody } from "./readout";
export function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState("");
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);
  const [output, setOutput] = useState<Row | null>(null);
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!API || !file) return;
    setPending(true);
    setError("");
    const body = new FormData();
    body.append("file", file);
    body.append("name", name || file.name.replace(/\.csv$/i, ""));
    try {
      setOutput(
        await api("/api/upload", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token || (/^http:\/\/(localhost|127\.0\.0\.1)(:|\/)/.test(API) ? "local-development-only-change-me" : "")}`,
          },
          body,
        }),
      );
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "The CSV could not be analyzed.",
      );
    } finally {
      setPending(false);
    }
  }
  if (output?.manifest)
    return (
      <>
        <div className="session-banner">
          <span>Session readout · uploaded data</span>
          <div>
            <a
              className="button small"
              href={`data:text/markdown;charset=utf-8,${encodeURIComponent(str(output.markdown, ""))}`}
              download="uploaded-readout.md"
            >
              Download Markdown
            </a>
            <a
              className="button small"
              href={`data:text/html;charset=utf-8,${encodeURIComponent(str(output.html, ""))}`}
              download="uploaded-readout.html"
            >
              Download HTML
            </a>
            <button className="button small" onClick={() => setOutput(null)}>
              Analyze another CSV
            </button>
          </div>
        </div>
        <ReadoutBody manifest={output.manifest as Manifest} session />
      </>
    );
  return (
    <>
      <PageHead
        eyebrow="BRING YOUR OWN EXPERIMENT"
        title="From unit-level data to a readout."
        description="Upload assignments and outcomes. The platform checks health before computing a result."
      />
      <div className="upload-layout">
        <form
          className="input-card"
          onSubmit={submit}
          aria-describedby={!API ? "upload-api-notice" : undefined}
        >
          <div className="panel-title">
            <h2>Experiment data</h2>
            <span className="tag">CSV</span>
          </div>
          {!API && (
            <div className="notice" id="upload-api-notice" role="status">
              <p>
                This published view shows stored results. CSV analysis needs a
                connected live API, which is not configured for this view.
              </p>
            </div>
          )}
          <label className="upload-zone">
            <Icon name="upload" size={30} />
            <strong>{file ? file.name : "Choose your experiment CSV"}</strong>
            <span>One row per randomization unit</span>
            <input
              type="file"
              accept=".csv,text/csv"
              required
              disabled={!API}
              aria-label="Choose experiment CSV"
              onChange={(e) => {
                setFile(e.target.files?.[0] ?? null);
                setError("");
              }}
            />
          </label>
          <label className="text-field">
            Experiment name
            <input
              value={name}
              disabled={!API}
              placeholder="Checkout conversion experiment"
              onChange={(e) => setName(e.target.value)}
            />
          </label>
          <label className="text-field">
            Demo write token
            <input
              type="password"
              value={token}
              disabled={!API}
              placeholder="Local default or deployed API token"
              autoComplete="off"
              onChange={(e) => setToken(e.target.value)}
            />
          </label>
          <div className="notice">
            <p>
              The token authorizes an analysis request. It stays in this page
              session and is sent only to the configured API.
            </p>
          </div>
          <button
            className="button primary full"
            disabled={!API || pending || !file}
          >
            {pending
              ? "Running health checks and analysis..."
              : "Analyze and create readout"}
            <Icon name="arrow" size={16} />
          </button>
          {pending && (
            <div
              className="skeleton upload-skeleton"
              aria-label="Analysis running"
            />
          )}
          {error && (
            <div className="inline-error" role="alert">
              {error}
            </div>
          )}
        </form>
        <div className="upload-guide">
          <span className="mini-label">EXPECTED COLUMNS</span>
          <h2>A small, explicit data contract.</h2>
          <dl>
            <dt>
              unit_id <b>required</b>
            </dt>
            <dd>A unique identifier for the randomized unit.</dd>
            <dt>
              variant <b>required</b>
            </dt>
            <dd>
              <code>control</code> or <code>treatment</code>.
            </dd>
            <dt>
              value <b>required</b>
            </dt>
            <dd>The primary outcome, as a numeric value.</dd>
            <dt>
              exposed <b>optional</b>
            </dt>
            <dd>Whether the assigned unit was exposed. Defaults to true.</dd>
            <dt>
              day, segment, pre_value <b>optional</b>
            </dt>
            <dd>Observation day, segment label, and a pre-period covariate.</dd>
          </dl>
          <pre>
            unit_id,variant,value,exposed
            <br />
            u001,control,0,true
            <br />
            u002,treatment,1,true
          </pre>
          <p className="caption">
            The example shows the format only. It is not sufficient data for an
            experiment.
          </p>
        </div>
      </div>
    </>
  );
}
