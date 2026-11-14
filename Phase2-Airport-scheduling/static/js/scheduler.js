
/* =========================================================
   INTELLIGENT AIRPORT RUNWAY SCHEDULING SYSTEM
   File: static/js/scheduler.js
   ========================================================= */

"use strict";

/* ======================== STATE ======================== */

let selectedAirportId = null;
let allWaitingFlights = [];
let isSchedulerRunning = false;
let previewRequestId = 0;

/* ===================== DOM ELEMENTS ==================== */

const airportSelect = document.getElementById("airportSelect");
const algorithmSelect = document.getElementById("algorithmSelect");
const quantumGroup = document.getElementById("quantumGroup");
const timeQuantum = document.getElementById("timeQuantum");
const runSchedulerBtn = document.getElementById("runSchedulerBtn");
const compareAllAlgorithmsBtn = document.getElementById(
    "compareAllAlgorithmsBtn"
);

const flightsLoading = document.getElementById("flightsLoading");
const flightsTableWrapper = document.getElementById("flightsTableWrapper");
const flightsTableBody = document.getElementById("flightsTableBody");
const flightCountBadge = document.getElementById("flightCountBadge");

const resultSection = document.getElementById("resultSection");
const schedulerLoading = document.getElementById("schedulerLoading");

/* ===================== INITIALIZATION ================= */

document.addEventListener("DOMContentLoaded", async () => {
    bindEvents();
    createAlgorithmPreviewSection();
    createRoundRobinTimelineSection();

    await loadAirports();
    await loadAlgorithms();

    if (airportSelect?.value) {
        selectedAirportId = airportSelect.value;
        await loadWaitingFlights(selectedAirportId);
    }

    updateQuantumVisibility();
    renderAlgorithmPreview();
});

/* ====================== EVENT LISTENERS ================ */

function bindEvents() {
    airportSelect?.addEventListener("change", async () => {
        selectedAirportId = airportSelect.value || null;
        clearPreviousResult();

        if (selectedAirportId) {
            await loadWaitingFlights(selectedAirportId);
        } else {
            allWaitingFlights = [];
            renderOriginalFlights();
            renderAlgorithmPreview();
            showFlightsMessage("Select an airport to load flights.");
        }
    });

    algorithmSelect?.addEventListener("change", () => {
        updateQuantumVisibility();
        renderAlgorithmPreview();
    });

    timeQuantum?.addEventListener("input", renderAlgorithmPreview);
    runSchedulerBtn?.addEventListener("click", runSelectedScheduler);
    compareAllAlgorithmsBtn?.addEventListener(
        "click",
        compareAllAlgorithms
    );
}

/* ======================== LOAD AIRPORTS ================= */

async function loadAirports() {
    if (!airportSelect) return;

    try {
        const response = await fetch("/airports");
        const data = await readResponse(response);

        const airports = Array.isArray(data)
            ? data
            : Array.isArray(data.airports)
                ? data.airports
                : Array.isArray(data.data)
                    ? data.data
                    : [];

        airportSelect.innerHTML =
            '<option value="">Select Airport</option>';

        airports.forEach((airport) => {
            const id = airport.airport_id ?? airport.id;
            if (id == null) return;

            const option = document.createElement("option");
            option.value = id;
            option.textContent =
                `${airport.airport_code || "AIRPORT"} - ` +
                `${airport.airport_name || airport.name || "Unnamed Airport"}`;

            airportSelect.appendChild(option);
        });

        if (!airports.length) {
            selectedAirportId = null;
            showToast("No airports found. Add an airport first.", "error");
            return;
        }

        if (!airportSelect.value) {
            airportSelect.value =
                airports[0].airport_id ?? airports[0].id;
        }

        selectedAirportId = airportSelect.value || null;
    } catch (error) {
        console.error("Airport loading error:", error);
        showToast(error.message || "Unable to load airports.", "error");
    }
}

/* ======================== LOAD ALGORITHMS =============== */

async function loadAlgorithms() {
    if (!algorithmSelect) return;

    const fallbackAlgorithms = [
        { value: "FCFS", label: "First Come First Served (FCFS)" },
        { value: "SJF", label: "Shortest Job First (SJF)" },
        { value: "SRTF", label: "Shortest Remaining Time First (SRTF)" },
        { value: "PRIORITY", label: "Priority Scheduling" },
        { value: "ROUND_ROBIN", label: "Round Robin (RR)" },
        { value: "HRRN", label: "Highest Response Ratio Next (HRRN)" },
        { value: "MLQ", label: "Multilevel Queue (MLQ)" },
        { value: "MLFQ", label: "Multilevel Feedback Queue (MLFQ)" }
    ];

    try {
        let algorithms = [];

        if (typeof getAlgorithms === "function") {
            const data = await getAlgorithms();

            algorithms = Array.isArray(data)
                ? data
                : Array.isArray(data?.algorithms)
                    ? data.algorithms
                    : Array.isArray(data?.data)
                        ? data.data
                        : [];
        }

        if (!algorithms.length) algorithms = fallbackAlgorithms;

        const previousValue = algorithmSelect.value;
        algorithmSelect.innerHTML =
            '<option value="">Select Algorithm</option>';

        algorithms.forEach((item) => {
            const rawValue = typeof item === "string"
                ? item
                : item.value ||
                  item.algorithm ||
                  item.algorithm_name ||
                  item.name;

            if (!rawValue) return;

            const value = String(rawValue).trim().toUpperCase();

            const label = typeof item === "string"
                ? formatAlgorithmName(value)
                : item.label ||
                  item.display_name ||
                  item.name ||
                  formatAlgorithmName(value);

            const option = document.createElement("option");
            option.value = value;
            option.textContent = label;
            algorithmSelect.appendChild(option);
        });

        if (
            previousValue &&
            [...algorithmSelect.options].some(
                option => option.value === previousValue
            )
        ) {
            algorithmSelect.value = previousValue;
        }
    } catch (error) {
        console.error("Algorithm loading error:", error);

        algorithmSelect.innerHTML =
            '<option value="">Select Algorithm</option>';

        fallbackAlgorithms.forEach(({ value, label }) => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = label;
            algorithmSelect.appendChild(option);
        });
    }

    updateQuantumVisibility();
    renderAlgorithmPreview();
}

/* ======================= WAITING FLIGHTS ================ */

async function loadWaitingFlights(airportId) {
    if (!airportId) return;

    showFlightsMessage("Loading waiting flights...");

    try {
        let data;

        if (typeof getFlights === "function") {
            data = await getFlights(airportId);
        } else {
            const response = await fetch(
                `/scheduler/flights?airport_id=${encodeURIComponent(airportId)}`
            );
            data = await readResponse(response);
        }

        const flights = Array.isArray(data)
            ? data
            : Array.isArray(data?.flights)
                ? data.flights
                : Array.isArray(data?.data)
                    ? data.data
                    : [];

        allWaitingFlights = flights.filter((flight) => {
            const status = String(flight.status || "").toUpperCase();
            return ["WAITING", "EMERGENCY"].includes(status);
        });

        renderOriginalFlights();
        renderAlgorithmPreview();
    } catch (error) {
        console.error("Flight loading error:", error);

        allWaitingFlights = [];
        renderOriginalFlights();
        renderAlgorithmPreview();

        showFlightsMessage(
            error.message || "Unable to load waiting flights."
        );

        showToast("Unable to load waiting flights.", "error");
    }
}

/* ======================= ORIGINAL FLIGHTS TABLE ========= */

function renderOriginalFlights() {
    if (!flightsTableBody) return;

    flightsTableBody.innerHTML = "";

    if (flightCountBadge) {
        flightCountBadge.textContent =
            `${allWaitingFlights.length} Flight` +
            `${allWaitingFlights.length === 1 ? "" : "s"}`;
    }

    if (!allWaitingFlights.length) {
        showFlightsMessage("No waiting flights found for this airport.");
        return;
    }

    allWaitingFlights.forEach((flight, index) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>
                <strong>${escapeHtml(getFlightLabel(flight))}</strong>
                <br>
                <small>${escapeHtml(flight.airline_name || "Unknown airline")}</small>
            </td>
            <td>${escapeHtml(flight.operation_type || flight.flight_type || "-")}</td>
            <td>${getSituationBadge(flight.current_situation || flight.situation)}</td>
            <td>${formatNumber(flight.processing_time_minutes ?? flight.duration_minutes, 10)} min</td>
            <td>${formatNullable(flight.fuel_percentage)}${flight.fuel_percentage != null ? "%" : ""}</td>
            <td>${formatNullable(flight.passenger_count)}</td>
            <td>${getStatusBadge(flight.status)}</td>
        `;

        flightsTableBody.appendChild(row);
    });

    if (flightsLoading) flightsLoading.style.display = "none";
    if (flightsTableWrapper) flightsTableWrapper.style.display = "block";
}

/* ======================= ALGORITHM PREVIEW ============== */

function createAlgorithmPreviewSection() {
    if (document.getElementById("algorithmPreviewSection")) return;

    const section = document.createElement("section");
    section.id = "algorithmPreviewSection";
    section.className = "card";
    section.style.marginTop = "20px";

    section.innerHTML = `
        <div class="section-heading">
            <div>
                <h2>Algorithm Queue Preview</h2>
                <p>
                    Preview how the selected algorithm orders waiting flights.
                    This does not allocate runways or change flight status.
                </p>
            </div>
        </div>

        <div id="algorithmPreviewMessage" class="empty-state">
            Select an airport and algorithm to preview the queue.
        </div>

        <div id="algorithmPreviewTableWrapper"
             class="table-container" style="display:none;">
            <table>
                <thead>
                    <tr>
                        <th>Queue Position</th>
                        <th>Flight</th>
                        <th>Situation</th>
                        <th>Processing Time</th>
                        <th>Request Time</th>
                        <th>Preview Rule</th>
                    </tr>
                </thead>
                <tbody id="algorithmPreviewTableBody"></tbody>
            </table>
        </div>
    `;

    const waitingCard = flightsTableWrapper?.closest(".card");

    if (waitingCard?.parentNode) {
        waitingCard.parentNode.insertBefore(section, waitingCard.nextSibling);
    } else {
        document.querySelector(".scheduler-page")?.appendChild(section);
    }
}

async function renderAlgorithmPreview() {
    const message = document.getElementById("algorithmPreviewMessage");
    const wrapper = document.getElementById("algorithmPreviewTableWrapper");
    const tbody = document.getElementById("algorithmPreviewTableBody");

    if (!message || !wrapper || !tbody) return;

    const requestId = ++previewRequestId;
    tbody.innerHTML = "";

    const algorithm = String(
        algorithmSelect?.value || ""
    ).trim().toUpperCase();

    if (!selectedAirportId) {
        message.style.display = "block";
        message.textContent = "Select an airport to preview its waiting queue.";
        wrapper.style.display = "none";
        return;
    }

    if (!algorithm) {
        message.style.display = "block";
        message.textContent = "Select a scheduling algorithm to preview the queue.";
        wrapper.style.display = "none";
        return;
    }

    if (!allWaitingFlights.length) {
        message.style.display = "block";
        message.textContent = "There are no waiting flights to preview.";
        wrapper.style.display = "none";
        return;
    }

    if (!["FCFS", "SJF", "PRIORITY", "ROUND_ROBIN"].includes(algorithm)) {
        message.style.display = "block";
        message.textContent =
            `${formatAlgorithmName(algorithm)} preview is not implemented. ` +
            "Use Run Scheduler to request backend execution.";
        wrapper.style.display = "none";
        return;
    }

    const quantum = Number(timeQuantum?.value || 3);
    if (algorithm === "ROUND_ROBIN" &&
        (!Number.isFinite(quantum) || quantum <= 0)) {
        message.style.display = "block";
        message.textContent =
            "Enter a valid positive time quantum for Round Robin.";
        wrapper.style.display = "none";
        return;
    }

    message.style.display = "block";
    message.textContent = "Calculating queue order...";
    wrapper.style.display = "none";

    try {
        const response = await fetch(
            `/scheduler/preview/${encodeURIComponent(selectedAirportId)}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    algorithm,
                    time_quantum: quantum
                })
            }
        );
        const result = await readResponse(response);
        if (requestId !== previewRequestId) return;

        tbody.innerHTML = "";
        result.queue.forEach((flight) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td><strong>${flight.queue_position}</strong></td>
                <td>${escapeHtml(getFlightLabel(flight))}</td>
                <td>${getSituationBadge(flight.situation)}</td>
                <td>${formatNumber(flight.processing_time, 10)} min</td>
                <td>${escapeHtml(formatDateTime(flight.requested_time))}</td>
                <td>${escapeHtml(formatAlgorithmName(algorithm))}</td>
            `;
            tbody.appendChild(row);
        });

        const invalidCount = result.invalid_flights?.length || 0;
        if (!result.queue.length) {
            message.textContent = invalidCount
                ? result.invalid_flights.map(item => item.reason).join("; ")
                : "There are no waiting flights to preview.";
            wrapper.style.display = "none";
            return;
        }

        message.style.display = invalidCount ? "block" : "none";
        message.textContent = invalidCount
            ? `${invalidCount} flight(s) omitted: ` +
                result.invalid_flights.map(item => item.reason).join("; ")
            : "";
        wrapper.style.display = "block";
    } catch (error) {
        if (requestId !== previewRequestId) return;
        message.style.display = "block";
        message.textContent =
            error.message || "Unable to calculate the preview queue.";
        wrapper.style.display = "none";
    }
}

async function compareAllAlgorithms() {
    if (!selectedAirportId) {
        showToast("Please select an airport first.", "error");
        return;
    }

    if (compareAllAlgorithmsBtn) {
        compareAllAlgorithmsBtn.disabled = true;
        compareAllAlgorithmsBtn.textContent = "Comparing...";
    }

    try {
        const response = await fetch(
            `/scheduler/preview/all/${encodeURIComponent(selectedAirportId)}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    time_quantum: Number(timeQuantum?.value || 3)
                })
            }
        );
        const result = await readResponse(response);
        renderAllAlgorithmGanttCharts(result);
        document.getElementById("ganttPrintReport")?.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    } catch (error) {
        console.error("Unable to compare scheduling algorithms:", error);
        showToast(
            error.message || "Unable to compare scheduling algorithms.",
            "error"
        );
    } finally {
        if (compareAllAlgorithmsBtn) {
            compareAllAlgorithmsBtn.disabled = false;
            compareAllAlgorithmsBtn.textContent = "Compare All Algorithms";
        }
    }
}

function renderAllAlgorithmGanttCharts(result) {
    let report = document.getElementById("ganttPrintReport");
    if (!report) {
        report = document.createElement("section");
        report.id = "ganttPrintReport";
        report.className = "gantt-print-report";
        document.querySelector(".scheduler-page")?.appendChild(report);
    }

    const airportName =
        airportSelect?.selectedOptions?.[0]?.textContent?.trim() ||
        `Airport ${result.airport_id}`;
    const invalidFlights = Array.isArray(result.invalid_flights)
        ? result.invalid_flights
        : [];
    const charts = Array.isArray(result.charts) ? result.charts : [];
    const inputFlights = Array.isArray(result.input_flights)
        ? result.input_flights
        : [];

    report.innerHTML = `
        <header class="gantt-print-header">
            <h1>Algorithm Comparison (Same Flight Set)</h1>
            <p>${escapeHtml(airportName)}</p>
            <p>
                Read-only simulation using the same ${escapeHtml(result.flight_count)}
                active flight record(s) for all algorithms. No schedules are saved,
                resources allocated, or flight statuses changed.
            </p>
            <p>Round Robin time quantum: ${escapeHtml(result.time_quantum)} min</p>
            <p class="comparison-flight-list">
                Input flights:
                ${inputFlights.map(flight =>
                    escapeHtml(flight.flight_number || `#${flight.flight_id}`)
                ).join(", ") || "None"}
            </p>
            <button type="button" id="printComparisonReportBtn" class="btn btn-secondary">
                Print Comparison
            </button>
        </header>
        ${invalidFlights.length ? `
            <div class="gantt-print-invalid">
                ${invalidFlights.map(item =>
                    `<p>${escapeHtml(item.flight_number || item.flight_id || "Flight")}:
                    ${escapeHtml(item.reason || "Invalid flight data")}</p>`
                ).join("")}
            </div>
        ` : ""}
        ${Number(result.flight_count) === 0 ? `
            <p class="comparison-empty">
                No waiting, scheduled, or in-progress flights were found for
                this airport, so the algorithm metrics are zero.
            </p>
        ` : ""}
        <div class="table-container comparison-metrics">
            <table>
                <thead>
                    <tr>
                        <th>Algorithm</th>
                        <th>Flights</th>
                        <th>Avg Waiting</th>
                        <th>Avg Turnaround</th>
                        <th>Avg Response</th>
                        <th>Throughput</th>
                        <th>Busy-time Utilization</th>
                    </tr>
                </thead>
                <tbody>
                    ${charts.map(chart => `
                        <tr>
                            <td>${escapeHtml(formatAlgorithmName(chart.algorithm))}</td>
                            <td>${formatNumber(chart.metrics?.total_flights, 0)}</td>
                            <td>${formatNumber(chart.metrics?.average_waiting_time, 0)} min</td>
                            <td>${formatNumber(chart.metrics?.average_turnaround_time, 0)} min</td>
                            <td>${formatNumber(chart.metrics?.average_response_time, 0)} min</td>
                            <td>${formatNumber(chart.metrics?.throughput, 0)} flights/min</td>
                            <td>${formatNumber(chart.metrics?.runway_utilization, 0)}%</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        </div>
        ${charts.map(chart => renderAlgorithmGanttChart(chart)).join("")}
    `;

    report.querySelector("#printComparisonReportBtn")?.addEventListener(
        "click",
        () => window.print()
    );
}

function renderAlgorithmGanttChart(chart) {
    const segments = Array.isArray(chart.segments) ? chart.segments : [];
    const timeValues = segments.flatMap(segment => [
        new Date(segment.start_time).getTime(),
        new Date(segment.end_time).getTime()
    ]).filter(Number.isFinite);
    const chartStart = Math.min(...timeValues);
    const chartEnd = Math.max(...timeValues);
    const totalDuration = chartEnd - chartStart;
    const colorByFlight = new Map();
    const colors = [
        "#2563eb", "#059669", "#d97706", "#7c3aed",
        "#db2777", "#0891b2", "#4f46e5", "#65a30d"
    ];

    const blocks = segments.map(segment => {
        const start = new Date(segment.start_time).getTime();
        const end = new Date(segment.end_time).getTime();
        if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) {
            return "";
        }

        const flightKey = String(segment.flight_id);
        if (!colorByFlight.has(flightKey)) {
            colorByFlight.set(flightKey, colors[colorByFlight.size % colors.length]);
        }

        const left = ((start - chartStart) / totalDuration) * 100;
        const width = ((end - start) / totalDuration) * 100;
        const label = segment.flight_number ||
            `Flight #${segment.flight_id}`;

        return `
            <div class="gantt-segment"
                 style="left:${left}%;width:${width}%;background:${colorByFlight.get(flightKey)}"
                 title="${escapeHtml(label)}: ${escapeHtml(formatDateTime(segment.start_time))} – ${escapeHtml(formatDateTime(segment.end_time))}">
                ${escapeHtml(label)}
            </div>
        `;
    }).join("");

    const detailRows = segments.map(segment => `
        <tr>
            <td>${escapeHtml(segment.flight_number || `Flight #${segment.flight_id}`)}</td>
            <td>${escapeHtml(segment.turn_number ?? 1)}</td>
            <td>${escapeHtml(formatDateTime(segment.start_time))}</td>
            <td>${escapeHtml(formatDateTime(segment.end_time))}</td>
            <td>${formatNumber(segment.duration_minutes, 0)} min</td>
        </tr>
    `).join("");

    return `
        <section class="gantt-print-algorithm">
            <h2>${escapeHtml(formatAlgorithmName(chart.algorithm))}</h2>
            ${segments.length && totalDuration > 0 ? `
                <div class="gantt-chart-track">${blocks}</div>
                <div class="gantt-chart-axis">
                    <span>${escapeHtml(formatDateTime(new Date(chartStart).toISOString()))}</span>
                    <span>${escapeHtml(formatDateTime(new Date(chartEnd).toISOString()))}</span>
                </div>
                <div class="table-container gantt-detail-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Flight</th>
                                <th>Segment</th>
                                <th>Start</th>
                                <th>End</th>
                                <th>Duration</th>
                            </tr>
                        </thead>
                        <tbody>${detailRows}</tbody>
                    </table>
                </div>
            ` : '<p class="empty-state">No valid execution segments.</p>'}
        </section>
    `;
}

/* ======================= SCHEDULING TIMELINE ============ */

function createRoundRobinTimelineSection() {
    if (document.getElementById("roundRobinTimelineSection")) return;

    const section = document.createElement("section");
    section.id = "roundRobinTimelineSection";
    section.className = "card";
    section.style.marginTop = "20px";
    section.style.display = "none";

    section.innerHTML = `
        <div class="section-heading">
            <div>
                <h2>Scheduling Gantt Timeline</h2>
                <p>Each row represents one scheduling execution segment.</p>
            </div>
            <span id="rrTurnCount" class="badge badge-info">0 Turns</span>
        </div>

        <div id="rrTimelineSummary" style="margin:12px 0;color:#64748b;"></div>

        <h3 class="gantt-sequence-title">Gantt chart</h3>
        <div id="rrGanttChart" class="gantt-sequence-track"></div>
        <div id="rrGanttTimeAxis" class="gantt-sequence-axis"></div>

        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>Global Turn</th>
                        <th>Flight</th>
                        <th>Flight Turn</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Duration</th>
                        <th>Remaining</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="rrTimelineTableBody"></tbody>
            </table>
        </div>
    `;

    if (resultSection?.parentNode) {
        resultSection.parentNode.insertBefore(
            section,
            resultSection.nextSibling
        );
    } else {
        document.querySelector(".scheduler-page")?.appendChild(section);
    }
}

function renderRoundRobinTimeline(result) {
    const section = document.getElementById("roundRobinTimelineSection");
    const tbody = document.getElementById("rrTimelineTableBody");
    const countBadge = document.getElementById("rrTurnCount");
    const summary = document.getElementById("rrTimelineSummary");
    const ganttChart = document.getElementById("rrGanttChart");
    const ganttTimeAxis = document.getElementById("rrGanttTimeAxis");

    if (!section || !tbody) return;

    tbody.innerHTML = "";
    if (ganttChart) ganttChart.innerHTML = "";
    if (ganttTimeAxis) ganttTimeAxis.innerHTML = "";

    const algorithm = String(
        result?.algorithm || algorithmSelect?.value || ""
    ).trim().toUpperCase();

    if (![
        "FCFS", "SJF", "SRTF", "PRIORITY",
        "ROUND_ROBIN", "HRRN", "MLQ", "MLFQ"
    ].includes(algorithm)) {
        section.style.display = "none";
        return;
    }

    section.style.display = "block";

    const quantum = Number(
        result?.time_quantum ?? timeQuantum?.value ?? 3
    );

    // Prefer the global chronological timeline from the backend.
    let turns = Array.isArray(result?.execution_timeline)
        ? result.execution_timeline.map(turn => ({ ...turn }))
        : [];

    // Fallback to execution_slices nested under scheduled flights.
    if (turns.length === 0) {
        const scheduled = getScheduledFlights(result);

        scheduled.forEach(flight => {
            const slices = Array.isArray(flight.execution_slices)
                ? flight.execution_slices
                : [];

            slices.forEach((slice, index) => {
                turns.push({
                    flight_id: flight.flight_id,
                    flight_number: flight.flight_number,
                    turn_number: slice.turn_number ?? index + 1,
                    start_time: slice.start_time,
                    end_time: slice.end_time,
                    duration_minutes: slice.duration_minutes,
                    remaining_time_minutes: slice.remaining_time_minutes,
                    completed: slice.completed
                });
            });
        });
    }

    if (turns.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8">
                    No execution turns were returned by the backend.
                    Check execution_slices in round_robin.py and
                    execution_timeline in the scheduler API response.
                </td>
            </tr>
        `;

        if (countBadge) countBadge.textContent = "0 Turns";

        if (summary) {
            summary.textContent =
                (algorithm === "ROUND_ROBIN"
                    ? `Quantum: ${Number.isFinite(quantum) ? quantum : "-"} min. `
                    : "") +
                "The backend returned no execution segments.";
        }
        if (ganttChart) {
            ganttChart.innerHTML =
                '<span class="gantt-sequence-empty">No execution segments</span>';
        }

        console.warn("No scheduling execution segments returned.", result);
        return;
    }

    // Sort in actual simulated execution order.
    turns.sort((a, b) => {
        const timeA = a.start_time
            ? new Date(a.start_time).getTime()
            : Number.MAX_SAFE_INTEGER;

        const timeB = b.start_time
            ? new Date(b.start_time).getTime()
            : Number.MAX_SAFE_INTEGER;

        if (timeA !== timeB) return timeA - timeB;

        return Number(a.turn_number || 0) -
            Number(b.turn_number || 0);
    });

    const colors = [
        "#149b85", "#2878c7", "#8050b7", "#bf526c",
        "#bd7b18", "#1689a2", "#5965c9", "#65952b"
    ];
    const colorByFlight = new Map();
    const chartSegments = [];
    let previousEnd = null;

    turns.forEach(turn => {
        const start = new Date(turn.start_time);
        const end = new Date(turn.end_time);
        const startMs = start.getTime();
        const endMs = end.getTime();
        if (!Number.isFinite(startMs) || !Number.isFinite(endMs) || endMs <= startMs) {
            return;
        }

        if (previousEnd != null && startMs > previousEnd) {
            chartSegments.push({
                flight_number: "IDLE",
                start_time: new Date(previousEnd).toISOString(),
                end_time: turn.start_time,
                duration_minutes: (startMs - previousEnd) / 60000,
                idle: true
            });
        }

        chartSegments.push({
            ...turn,
            duration_minutes: (endMs - startMs) / 60000
        });
        previousEnd = Math.max(previousEnd || endMs, endMs);
    });

    chartSegments.forEach(segment => {
        const flightKey = String(segment.flight_id ?? segment.flight_number);
        if (!segment.idle && !colorByFlight.has(flightKey)) {
            colorByFlight.set(flightKey, colors[colorByFlight.size % colors.length]);
        }

        const block = document.createElement("div");
        block.className = segment.idle
            ? "gantt-sequence-block gantt-sequence-idle"
            : "gantt-sequence-block";
        const duration = Math.max(0.01, Number(segment.duration_minutes) || 0);
        block.style.flexGrow = String(duration);
        if (!segment.idle) {
            block.style.backgroundColor = colorByFlight.get(flightKey);
        }

        const label = segment.flight_number ||
            `Flight #${segment.flight_id}`;
        block.textContent = segment.idle ? "IDLE" : label;
        block.title = segment.idle
            ? `Idle: ${formatGanttTime(segment.start_time)} - ${formatGanttTime(segment.end_time)}`
            : `${label}: ${formatGanttTime(segment.start_time)} - ${formatGanttTime(segment.end_time)}`;
        ganttChart?.appendChild(block);
    });

    if (ganttTimeAxis && chartSegments.length) {
        chartSegments.forEach(segment => {
            const startLabel = document.createElement("span");
            startLabel.className = "gantt-axis-start";
            startLabel.style.flexGrow = String(
                Math.max(0.01, Number(segment.duration_minutes) || 0)
            );
            startLabel.textContent = formatGanttTime(segment.start_time);
            ganttTimeAxis.appendChild(startLabel);
        });

        const finalLabel = document.createElement("span");
        finalLabel.className = "gantt-axis-end";
        finalLabel.textContent = formatGanttTime(
            chartSegments[chartSegments.length - 1].end_time
        );
        ganttTimeAxis.appendChild(finalLabel);
    }

    turns.forEach((turn, index) => {
        const row = document.createElement("tr");

        const flightLabel =
            turn.flight_number ||
            (turn.flight_id != null
                ? `Flight #${turn.flight_id}`
                : "Unknown flight");

        const duration = Number(turn.duration_minutes);
        const remaining = turn.remaining_time_minutes;

        const completed = turn.completed === true ||
            (remaining != null && Number(remaining) <= 0);

        const statusBadge = completed
            ? '<span class="badge badge-success">COMPLETED</span>'
            : '<span class="badge badge-warning">IN PROGRESS / PREEMPTED</span>';

        row.innerHTML = `
            <td><strong>${index + 1}</strong></td>
            <td>${escapeHtml(flightLabel)}</td>
            <td>${escapeHtml(turn.turn_number ?? index + 1)}</td>
            <td>${escapeHtml(formatDateTime(turn.start_time))}</td>
            <td>${escapeHtml(formatDateTime(turn.end_time))}</td>
            <td>${Number.isFinite(duration) ? `${formatNumber(duration, 0)} min` : "-"}</td>
            <td>${remaining == null ? "-" : `${formatNumber(remaining, 0)} min`}</td>
            <td>${statusBadge}</td>
        `;

        tbody.appendChild(row);
    });

    if (countBadge) {
        countBadge.textContent =
            `${turns.length} Turn${turns.length === 1 ? "" : "s"}`;
    }

    if (summary) {
        const flightCount = new Set(
            turns.map(turn => String(turn.flight_id))
        ).size;

        summary.textContent =
            (algorithm === "ROUND_ROBIN"
                ? `Time Quantum: ${Number.isFinite(quantum) ? quantum : "-"} min | `
                : "") +
            `Flights represented: ${flightCount} | ` +
            `Execution segments: ${turns.length}`;
    }

    console.log("Scheduling timeline rendered:", turns.length, "segments");
}

function formatGanttTime(value) {
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

/* ======================= RUN SCHEDULER ================== */

async function runSelectedScheduler() {
    if (isSchedulerRunning) return;

    if (!selectedAirportId) {
        showToast("Please select an airport.", "error");
        return;
    }

    const algorithm = String(
        algorithmSelect?.value || ""
    ).trim().toUpperCase();

    if (!algorithm) {
        showToast("Please select a scheduling algorithm.", "error");
        return;
    }

    const allowedAlgorithms = [
        "FCFS", "SJF", "SRTF", "PRIORITY",
        "ROUND_ROBIN", "HRRN", "MLQ", "MLFQ"
    ];

    if (!allowedAlgorithms.includes(algorithm)) {
        showToast(`Unsupported algorithm: ${algorithm}`, "error");
        return;
    }

    const quantum = Number(timeQuantum?.value || 3);

    if (
        algorithm === "ROUND_ROBIN" &&
        (!Number.isFinite(quantum) || quantum <= 0)
    ) {
        showToast("Enter a valid positive time quantum.", "error");
        return;
    }

    try {
        isSchedulerRunning = true;
        setLoading(true);
        clearPreviousResult();

        const response = await fetch(
            `/scheduler/run/${encodeURIComponent(selectedAirportId)}`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify({
                    algorithm,
                    time_quantum: quantum,
                    quantum
                })
            }
        );

        const result = await readResponse(response);

        displaySchedulerResult(result);

        const scheduled = getScheduledFlights(result);
        const failed = getFailedFlights(result);

        if (failed.length > 0 && scheduled.length > 0) {
            showToast(
                `${formatAlgorithmName(algorithm)} completed with allocation issues.`,
                "error"
            );
        } else if (failed.length > 0 && scheduled.length === 0) {
            showToast(
                result.message ||
                `${formatAlgorithmName(algorithm)} returned no successful allocations.`,
                "error"
            );
        } else {
            showToast(
                result.message ||
                `${formatAlgorithmName(algorithm)} scheduling completed.`,
                "success"
            );
        }

        await loadWaitingFlights(selectedAirportId);
    } catch (error) {
        console.error(`${algorithm} scheduler execution error:`, error);

        showToast(
            error.message || `${formatAlgorithmName(algorithm)} failed.`,
            "error"
        );
    } finally {
        isSchedulerRunning = false;
        setLoading(false);
    }
}

/* ======================= RESULT DISPLAY ================= */

function displaySchedulerResult(result) {
    if (!resultSection) return;

    resultSection.style.display = "block";

    const scheduled = getScheduledFlights(result);
    const failed = getFailedFlights(result);

    const resultMessage = document.getElementById("resultMessage");
    const resultStatus = document.getElementById("resultStatus");

    if (resultMessage) {
        resultMessage.textContent =
            result.message ||
            `${formatAlgorithmName(result.algorithm || algorithmSelect?.value)} ` +
            `completed for airport ${result.airport_id ?? selectedAirportId}.` +
            (result.run_id != null ? ` Run ID: ${result.run_id}.` : "");
    }

    if (resultStatus) {
        resultStatus.textContent = failed.length
            ? "COMPLETED WITH ISSUES"
            : "COMPLETED";

        resultStatus.className = failed.length
            ? "badge badge-warning"
            : "badge badge-success";
    }

    const metrics = result.metrics || result.statistics || {};

    setText("scheduledCount", scheduled.length);
    setText("failedCount", failed.length);

    setText("avgWaiting", metricValue(
        metrics.avg_waiting_time ??
        metrics.average_waiting_time ??
        metrics.avg_waiting ??
        average(scheduled, ["waiting_time_minutes", "waiting_time"])
    ));

    setText("avgTurnaround", metricValue(
        metrics.avg_turnaround_time ??
        metrics.average_turnaround_time ??
        metrics.avg_turnaround ??
        average(scheduled, ["turnaround_time_minutes", "turnaround_time"])
    ));

    setText("avgResponse", metricValue(
        metrics.avg_response_time ??
        metrics.average_response_time ??
        metrics.avg_response ??
        average(scheduled, ["response_time_minutes", "response_time"])
    ));

    setText(
        "runwayUtilization",
        metrics.runway_utilization != null
            ? `${metricValue(metrics.runway_utilization)}%`
            : "-"
    );

    renderScheduledFlights(scheduled);
    renderFailedFlights(failed);
    renderRoundRobinTimeline(result);

    const failedSection = document.getElementById("failedSection");

    if (failedSection) {
        failedSection.style.display = failed.length ? "block" : "none";
    }

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

/* ======================= RESULT NORMALIZATION ========== */

function getScheduledFlights(result) {
    if (Array.isArray(result.scheduled)) return result.scheduled;
    if (Array.isArray(result.scheduled_flights)) return result.scheduled_flights;
    if (Array.isArray(result.successful_flights)) return result.successful_flights;

    if (Array.isArray(result.queue)) {
        return result.queue.filter(flight => {
            const status = String(flight.status || "").toUpperCase();
            return !["FAILED", "BLOCKED", "REJECTED"].includes(status);
        });
    }

    return [];
}

function getFailedFlights(result) {
    if (Array.isArray(result.failed)) return result.failed;
    if (Array.isArray(result.failed_flights_list)) return result.failed_flights_list;
    if (Array.isArray(result.errors)) return result.errors;
    return [];
}

/* ======================= SUCCESSFUL ALLOCATIONS ======= */

function renderScheduledFlights(flights) {
    const tbody = document.getElementById("scheduledTableBody");
    if (!tbody) return;

    tbody.innerHTML = "";

    if (!flights.length) {
        tbody.innerHTML = `
            <tr><td colspan="8">No successful allocations were returned.</td></tr>
        `;
        return;
    }

    flights.forEach((flight, index) => {
        const runway = typeof flight.runway === "object"
            ? flight.runway?.runway_code ||
              flight.runway?.runway_name ||
              flight.runway?.name
            : flight.runway;

        const atc = typeof flight.atc === "object"
            ? flight.atc?.controller_name ||
              flight.atc?.name ||
              flight.atc?.callsign
            : flight.atc;

        const startTime =
            flight.scheduled_start ||
            flight.start_time ||
            flight.start ||
            flight.scheduled_start_time;

        const endTime =
            flight.scheduled_end ||
            flight.completion_time ||
            flight.end_time ||
            flight.scheduled_end_time;

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${flight.queue_position ?? index + 1}</td>
            <td>${escapeHtml(getFlightLabel(flight))}</td>
            <td>${escapeHtml(runway || "-")}</td>
            <td>${escapeHtml(atc || "-")}</td>
            <td>${escapeHtml(formatDateTime(startTime))}</td>
            <td>${escapeHtml(formatDateTime(endTime))}</td>
            <td>${formatNumber(flight.waiting_time_minutes ?? flight.waiting_time, 0)} min</td>
            <td>${getStatusBadge(flight.status || "SCHEDULED")}</td>
        `;

        tbody.appendChild(row);
    });
}

/* ======================= FAILED ALLOCATIONS ============ */

function renderFailedFlights(flights) {
    const tbody = document.getElementById("failedTableBody");
    if (!tbody) return;

    tbody.innerHTML = "";

    if (!flights.length) {
        tbody.innerHTML = `
            <tr><td colspan="4">No failed allocations reported.</td></tr>
        `;
        return;
    }

    flights.forEach(item => {
        const flight = item.flight || item;

        const reason =
            item.reason ||
            item.error ||
            item.message ||
            item.failure_reason ||
            "No reason provided by backend";

        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${escapeHtml(getFlightLabel(flight))}</td>
            <td>${escapeHtml(item.stage || "SCHEDULING")}</td>
            <td>${escapeHtml(reason)}</td>
            <td>${getStatusBadge(item.status || "FAILED")}</td>
        `;

        tbody.appendChild(row);
    });
}

/* ======================= ALGORITHM HELPERS ============= */

function updateQuantumVisibility() {
    if (!quantumGroup) return;

    quantumGroup.style.display =
        String(algorithmSelect?.value || "").toUpperCase() === "ROUND_ROBIN"
            ? "block"
            : "none";
}

function getProcessingTime(flight) {
    const value = Number(
        flight.processing_time_minutes ??
        flight.duration_minutes ??
        flight.estimated_duration ??
        10
    );

    return Number.isFinite(value) && value > 0 ? value : 10;
}

function getNumericPriority(flight) {
    const value = Number(
        flight.flight_priority ??
        flight.priority ??
        flight.priority_level ??
        999
    );

    return Number.isFinite(value) ? value : 999;
}

function getSituationPriority(flight) {
    const priorities = {
        MEDICAL: 1,
        EMERGENCY: 2,
        LOW_FUEL: 3,
        WEATHER: 4,
        VIP: 5,
        NORMAL: 6
    };

    const situation = String(
        flight.current_situation || flight.situation || "NORMAL"
    ).toUpperCase();

    return priorities[situation] ?? 6;
}

function compareRequestTime(a, b) {
    const timeA = getRequestTimestamp(a);
    const timeB = getRequestTimestamp(b);

    if (timeA !== timeB) return timeA - timeB;

    return String(getFlightLabel(a)).localeCompare(
        String(getFlightLabel(b))
    );
}

function getRequestTimestamp(flight) {
    const operation = String(
        flight.operation_type || flight.flight_type || ""
    ).toUpperCase();

    const operationTime = operation === "ARRIVAL"
        ? flight.arrival_time
        : flight.departure_time;

    const value =
        flight.request_time ||
        flight.created_at ||
        flight.scheduled_time ||
        operationTime ||
        flight.arrival_time ||
        flight.departure_time;

    if (!value) return Number.MAX_SAFE_INTEGER;

    const timestamp = new Date(value).getTime();

    return Number.isFinite(timestamp)
        ? timestamp
        : Number.MAX_SAFE_INTEGER;
}

function formatRequestTime(flight) {
    const operation = String(
        flight.operation_type || flight.flight_type || ""
    ).toUpperCase();

    const operationTime = operation === "ARRIVAL"
        ? flight.arrival_time
        : flight.departure_time;

    const value =
        flight.request_time ||
        flight.created_at ||
        flight.scheduled_time ||
        operationTime ||
        flight.arrival_time ||
        flight.departure_time;

    return value ? formatDateTime(value) : "Not available";
}

/* ======================= LABELS AND BADGES ============== */

function getFlightLabel(flight) {
    return (
        flight.flight_number ||
        flight.flight_code ||
        flight.callsign ||
        (flight.flight_id != null ? `Flight #${flight.flight_id}` : null) ||
        (flight.id != null ? `Flight #${flight.id}` : null) ||
        "Unknown flight"
    );
}

function getSituationBadge(situation) {
    const value = String(situation || "NORMAL").toUpperCase();

    const classes = {
        MEDICAL: "badge-danger",
        EMERGENCY: "badge-danger",
        LOW_FUEL: "badge-warning",
        WEATHER: "badge-warning",
        VIP: "badge-info",
        NORMAL: "badge-secondary"
    };

    return `
        <span class="badge ${classes[value] || "badge-secondary"}">
            ${escapeHtml(value.replaceAll("_", " "))}
        </span>
    `;
}

function getStatusBadge(status) {
    const value = String(status || "UNKNOWN").toUpperCase();

    const classes = {
        WAITING: "badge-warning",
        EMERGENCY: "badge-danger",
        SCHEDULED: "badge-success",
        COMPLETED: "badge-success",
        FAILED: "badge-danger",
        BLOCKED: "badge-danger",
        AVAILABLE: "badge-success",
        BUSY: "badge-warning"
    };

    return `
        <span class="badge ${classes[value] || "badge-secondary"}">
            ${escapeHtml(value.replaceAll("_", " "))}
        </span>
    `;
}

function formatAlgorithmName(value) {
    if (!value) return "Unknown Algorithm";

    const labels = {
        FCFS: "First Come First Served (FCFS)",
        SJF: "Shortest Job First (SJF)",
        SRTF: "Shortest Remaining Time First (SRTF)",
        PRIORITY: "Priority Scheduling",
        ROUND_ROBIN: "Round Robin (RR)",
        HRRN: "Highest Response Ratio Next (HRRN)",
        MLQ: "Multilevel Queue (MLQ)",
        MLFQ: "Multilevel Feedback Queue (MLFQ)"
    };

    const key = String(value).toUpperCase();

    return labels[key] || String(value).replaceAll("_", " ");
}

function formatDateTime(value) {
    if (!value) return "-";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return String(value);

    return date.toLocaleString();
}

function formatNullable(value) {
    return value == null || value === "" ? "-" : escapeHtml(value);
}

function formatNumber(value, fallback = 0) {
    if (value == null || value === "") return fallback;

    const number = Number(value);

    return Number.isFinite(number)
        ? number.toFixed(2).replace(/\.00$/, "")
        : fallback;
}

function metricValue(value) {
    if (value == null || value === "") return "-";

    const number = Number(value);

    return Number.isFinite(number)
        ? number.toFixed(2).replace(/\.00$/, "")
        : String(value);
}

function average(items, keys) {
    if (!items.length) return null;

    const values = items
        .map(item => {
            for (const key of keys) {
                if (item[key] != null && item[key] !== "") {
                    const number = Number(item[key]);
                    if (Number.isFinite(number)) return number;
                }
            }
            return null;
        })
        .filter(value => value != null);

    if (!values.length) return null;

    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

/* ======================= RESPONSE HELPERS =============== */

async function readResponse(response) {
    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok || data.success === false) {
        const details = data.error || data.message;

        throw new Error(
            details
                ? `${data.message || "Scheduler request failed"}: ${details}`
                : `Request failed with status ${response.status}`
        );
    }

    return data;
}

function showFlightsMessage(message) {
    if (flightsLoading) {
        flightsLoading.style.display = "block";
        flightsLoading.textContent = message;
    }

    if (flightsTableWrapper) {
        flightsTableWrapper.style.display = "none";
    }

    if (flightsTableBody) {
        flightsTableBody.innerHTML = "";
    }
}

function setLoading(isLoading) {
    if (schedulerLoading) {
        schedulerLoading.style.display = isLoading ? "flex" : "none";
    }

    if (runSchedulerBtn) {
        runSchedulerBtn.disabled = isLoading;
        runSchedulerBtn.textContent = isLoading
            ? "Running Scheduler..."
            : "Run Scheduler";
    }
}

function setText(id, value) {
    const element = document.getElementById(id);

    if (element) {
        element.textContent = value == null ? "-" : value;
    }
}

function clearPreviousResult() {
    if (resultSection) {
        resultSection.style.display = "none";
    }

    const timeline = document.getElementById(
        "roundRobinTimelineSection"
    );

    if (timeline) timeline.style.display = "none";
}

function showToast(message, type = "success") {
    const toast = document.getElementById("schedulerToast");

    if (!toast) {
        console.log(`[${type.toUpperCase()}] ${message}`);
        return;
    }

    toast.textContent = message;
    toast.className = `scheduler-toast ${type} show`;
    toast.style.display = "block";

    window.clearTimeout(showToast.timeoutId);

    showToast.timeoutId = window.setTimeout(() => {
        toast.classList.remove("show");
        toast.style.display = "none";
    }, 6000);
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
