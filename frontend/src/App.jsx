import { useEffect, useState } from "react";
import "./App.css";

const API =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8001";

function App() {
  const [campus, setCampus] = useState(null);
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  // ==========================================
  // LOAD CAMPUS STATE
  // ==========================================

  const loadCampusState = async () => {
    try {
      setError("");

      const response = await fetch(`${API}/campus-state`);

      if (!response.ok) {
        throw new Error("Backend unavailable");
      }

      const data = await response.json();

      setCampus(data);
    } catch (err) {
      setError(
        "Cannot connect to CampusFlow backend. Make sure FastAPI is running on port 8001."
      );
    }
  };

  // ==========================================
  // RUN AUTONOMOUS AGENT
  // ==========================================

  const runAgent = async () => {
    try {
      setRunning(true);
      setError("");
      setResult(null);

      const response = await fetch(`${API}/run-agent`, {
        method: "POST",
      });

      if (!response.ok) {
        throw new Error("Agent request failed");
      }

      const data = await response.json();

      setResult(data);

      // Reload the timetable after recovery.
      await loadCampusState();

    } catch (err) {
      setError(
        "CampusFlow could not execute the autonomous recovery."
      );
    } finally {
      setRunning(false);
    }
  };

  // ==========================================
  // INITIAL LOAD
  // ==========================================

  useEffect(() => {
    loadCampusState();
  }, []);

  // ==========================================
  // DERIVED DATA
  // ==========================================

  const disruptions =
    campus?.disruptions || [];

  const affectedClasses =
    result?.events
      ?.find(
        (event) =>
          event.label === "IMPACT INVESTIGATED"
      )
      ?.detail || "";

  const recoveryPlan =
    result?.recovery_plan ||
    campus?.recovery_plan ||
    [];

  const timetable =
    campus?.timetable?.classes || [];

  const highPriority =
    recoveryPlan.filter(
      (item) => item.priority >= 5
    ).length;

  const recoveryScore =
    recoveryPlan.reduce(
      (total, item) =>
        total + Math.max(0, item.score || 0),
      0
    );

  // ==========================================
  // AGENT EVENTS
  // ==========================================

  const events =
    result?.events || [];

  return (
    <div className="app">

      {/* =====================================
          HEADER
      ====================================== */}

      <header className="topbar">

        <div className="brand">

          <div className="brand-mark">
            CF
          </div>

          <div>
            <div className="brand-name">
              CampusFlow
            </div>

            <div className="brand-subtitle">
              AUTONOMOUS CAMPUS OPERATIONS
            </div>
          </div>

        </div>

        <div className="header-actions">

  <button
    className="reset-button"
    onClick={async () => {
      await fetch(`${API}/reset`, {
        method: "POST",
      });

      setResult(null);
      await loadCampusState();
    }}
  >
    RESET DEMO
  </button>

  <div className="agent-status">
    <span className="status-dot"></span>
    AGENT ONLINE
  </div>

</div>

      </header>


      <main className="container">

        {/* =====================================
            HERO
        ====================================== */}

        <section className="hero-grid">

          <div className="hero">

            <div className="eyebrow">
              CAMPUS OPERATIONS / LIVE
            </div>

            <h1>
              {running
                ? "Autonomous recovery in progress."
                : result?.status === "completed"
                ? "Campus disruption resolved."
                : "Your campus, operating itself."}
            </h1>

            <p>
              CampusFlow detects disruptions,
              evaluates constraints, plans recovery
              actions, executes decisions, and
              verifies the result.
            </p>

          </div>


          {/* INCIDENT CARD */}

          <div className="incident-card">

            <div className="incident-top">

              <span>
                ACTIVE INCIDENT
              </span>

              <span className="incident-id">
                {disruptions[0]?.id || "—"}
              </span>

            </div>

            <h2>
              {disruptions[0]?.type ===
              "college_suspension"
                ? `${disruptions[0]?.day} Suspension`
                : "Campus Disruption"}
            </h2>

            <p>
              {disruptions[0]?.reason ||
                "No active disruption"}
              {" · "}
              {affectedClasses ||
                `${campus?.affected_classes?.length || 0} classes affected`}
            </p>

            <div className="incident-divider"></div>

            <div className="recovery-required">
              <span className="orange-dot"></span>
              {result?.status === "completed"
                ? "RECOVERY COMPLETE"
                : "RECOVERY REQUIRED"}
            </div>

            <button
              className="primary-button"
              onClick={runAgent}
              disabled={running}
            >
              {running
                ? "AGENT WORKING..."
                : "RUN AUTONOMOUS RECOVERY"}
            </button>

          </div>

        </section>


        {/* =====================================
            STATS
        ====================================== */}

        <section className="stats-grid">

          <StatCard
            label="AFFECTED CLASSES"
            value={
              campus?.affected_classes?.length ||
              (result ? 6 : 0)
            }
          />

          <StatCard
            label="HIGH PRIORITY"
            value={String(highPriority).padStart(2, "0")}
          />

          <StatCard
            label="RECOVERY ACTIONS"
            value={recoveryPlan.length}
          />

          <StatCard
            label="DISRUPTION SCORE"
            value={recoveryScore}
          />

        </section>


        {/* =====================================
            ERROR
        ====================================== */}

        {error && (
          <div className="error-banner">
            ⚠ {error}
          </div>
        )}


        {/* =====================================
            AGENT + DECISION
        ====================================== */}

        <section className="two-column">

          <div className="panel">

            <div className="panel-header">

              <div>
                <div className="eyebrow">
                  AUTONOMOUS WORKFLOW
                </div>

                <h2>
                  Agent activity
                </h2>
              </div>

              <span
                className={
                  running
                    ? "panel-badge active"
                    : "panel-badge"
                }
              >
                {running
                  ? "RUNNING"
                  : result
                  ? "COMPLETED"
                  : "WAITING"}
              </span>

            </div>


            <div className="activity-list">

              {events.length === 0 ? (

                <div className="empty-state">
                  <div className="empty-icon">
                    ◉
                  </div>

                  <div>
                    Press{" "}
                    <strong>
                      RUN AUTONOMOUS RECOVERY
                    </strong>{" "}
                    to start the agent.
                  </div>
                </div>

              ) : (

                events.map((event, index) => (

                  <div
                    className="activity-item"
                    key={`${event.time}-${index}`}
                  >

                    <div className="activity-marker">
                      {event.status === "error"
                        ? "!"
                        : "✓"}
                    </div>

                    <div className="activity-content">

                      <div className="activity-title">
                        {event.label}
                      </div>

                      <div className="activity-detail">
                        {event.detail}
                      </div>

                    </div>

                    <div className="activity-time">
                      {event.time}
                    </div>

                  </div>

                ))

              )}

            </div>

          </div>


          {/* =====================================
              DECISION ENGINE
          ====================================== */}

          <div className="panel">

            <div className="panel-header">

              <div>

                <div className="eyebrow">
                  DECISION ENGINE
                </div>

                <h2>
                  Current decision
                </h2>

              </div>

              <span className="ai-badge">
                FEATHERLESS
              </span>

            </div>


            <div className="decision-body">

              {result ? (

                <>
                  <div className="decision-action">
                    <span className="decision-label">
                      FINAL ACTION
                    </span>

                    <strong>
                      {result.action}
                    </strong>
                  </div>

                  <div className="decision-message">
                    {result.message}
                  </div>

                  <div className="workflow-chain">

                    <WorkflowStep
                      text="DETECT"
                      done
                    />

                    <WorkflowArrow />

                    <WorkflowStep
                      text="INVESTIGATE"
                      done
                    />

                    <WorkflowArrow />

                    <WorkflowStep
                      text="PLAN"
                      done
                    />

                    <WorkflowArrow />

                    <WorkflowStep
                      text="REPLAN"
                      done
                    />

                    <WorkflowArrow />

                    <WorkflowStep
                      text="EXECUTE"
                      done
                    />

                    <WorkflowArrow />

                    <WorkflowStep
                      text="VERIFY"
                      done
                    />

                  </div>
                </>

              ) : (

                <div className="decision-empty">

                  <div className="decision-symbol">
                    AI
                  </div>

                  <h3>
                    Autonomous decision engine
                  </h3>

                  <p>
                    Featherless AI will determine
                    the next operational action while
                    CampusFlow enforces timetable and
                    resource constraints.
                  </p>

                </div>

              )}

            </div>

          </div>

        </section>


        {/* =====================================
            RECOVERY PLAN
        ====================================== */}

        <section className="panel recovery-panel">

          <div className="panel-header">

            <div>

              <div className="eyebrow">
                AUTONOMOUS RECOVERY
              </div>

              <h2>
                Dynamic recovery plan
              </h2>

            </div>

            <span className="panel-badge">
              {recoveryPlan.length} ACTIONS
            </span>

          </div>


          <div className="table-wrapper">

            <table>

              <thead>
                <tr>
                  <th>SUBJECT</th>
                  <th>FACULTY</th>
                  <th>ORIGINAL</th>
                  <th>NEW SLOT</th>
                  <th>PRIORITY</th>
                  <th>STATUS</th>
                </tr>
              </thead>

              <tbody>

                {recoveryPlan.length === 0 ? (

                  <tr>
                    <td
                      colSpan="6"
                      className="table-empty"
                    >
                      No recovery plan generated yet.
                    </td>
                  </tr>

                ) : (

                  recoveryPlan.map((item) => (

                    <tr key={item.class_id}>

                      <td>
                        <strong>
                          {item.subject}
                        </strong>
                      </td>

                      <td>
                        {item.faculty}
                      </td>

                      <td>
                        {item.original_day}
                        <br />
                        <span className="muted">
                          {item.original_slot}
                        </span>
                      </td>

                      <td>
                        <strong className="new-slot">
                          {item.recommended_day}
                          <br />
                          {item.recommended_slot}
                        </strong>
                      </td>

                      <td>
                        <span
                          className={
                            item.priority >= 5
                              ? "priority high"
                              : "priority"
                          }
                        >
                          P{item.priority}
                        </span>
                      </td>

                      <td>
                        <span className="success-status">
                          ✓ RECOVERED
                        </span>
                      </td>

                    </tr>

                  ))

                )}

              </tbody>

            </table>

          </div>

        </section>


        {/* =====================================
            DYNAMIC TIMETABLE
        ====================================== */}

        <section className="panel timetable-panel">

          <div className="panel-header">

            <div>

              <div className="eyebrow">
                LIVE CAMPUS STATE
              </div>

              <h2>
                Dynamic timetable
              </h2>

            </div>

            <span className="panel-badge active">
              LIVE
            </span>

          </div>


          <div className="timetable">

            {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].map(
              (day) => {

                const dayClasses =
                  timetable
                    .filter(
                      (item) =>
                        item.day === day
                    )
                    .sort((a, b) =>
                      a.slot.localeCompare(b.slot)
                    );

                return (
                  <div
                    className="day-column"
                    key={day}
                  >

                    <div className="day-header">
                      {day}
                    </div>

                    {dayClasses.length === 0 ? (

                      <div className="suspended">
                        SUSPENDED
                      </div>

                    ) : (

                      dayClasses.map((item) => (

                        <div
                          className="class-card"
                          key={item.id}
                        >

                          <div className="class-time">
                            {item.slot}
                          </div>

                          <div className="class-subject">
                            {item.subject}
                          </div>

                          <div className="class-meta">
                            {item.faculty}
                          </div>

                          <div className="class-room">
                            {item.room}
                          </div>

                        </div>

                      ))

                    )}

                  </div>
                );
              }
            )}

          </div>

        </section>


        {/* =====================================
            FOOTER
        ====================================== */}

        <footer>

          <div>
            CAMPUSFLOW
          </div>

          <div>
            AUTONOMOUS COLLEGE OPERATIONS
          </div>

          <div>
            POWERED BY FEATHERLESS AI
          </div>

        </footer>

      </main>

    </div>
  );
}


// ==========================================
// STAT CARD
// ==========================================

function StatCard({ label, value }) {

  return (
    <div className="stat-card">

      <div className="stat-label">
        {label}
      </div>

      <div className="stat-value">
        {value}
      </div>

    </div>
  );
}


// ==========================================
// WORKFLOW STEP
// ==========================================

function WorkflowStep({ text, done }) {

  return (
    <div
      className={
        done
          ? "workflow-step done"
          : "workflow-step"
      }
    >
      <span>
        {done ? "✓" : "○"}
      </span>

      {text}
    </div>
  );
}


// ==========================================
// WORKFLOW ARROW
// ==========================================

function WorkflowArrow() {

  return (
    <span className="workflow-arrow">
      →
    </span>
  );
}


export default App;