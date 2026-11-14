// =========================================================
// AIRPORT MANAGEMENT
// =========================================================

let airports = [];

let selectedAirportId = null;

let editingAirportId = null;

let currentResourceType = null;


// =========================================================
// DOM READY
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    async function () {

        setupAirportEvents();

        await loadAirports();

    }
);


// =========================================================
// EVENTS
// =========================================================

function setupAirportEvents() {

    // Add Airport

    document.getElementById(
        "addAirportBtn"
    ).addEventListener(
        "click",
        openAddAirportModal
    );


    document.getElementById(
        "emptyAddAirportBtn"
    ).addEventListener(
        "click",
        openAddAirportModal
    );


    // Close Airport Modal

    document.getElementById(
        "closeAirportModal"
    ).addEventListener(
        "click",
        closeAirportModal
    );


    document.getElementById(
        "cancelAirport"
    ).addEventListener(
        "click",
        closeAirportModal
    );


    // Airport Form

    document.getElementById(
        "airportForm"
    ).addEventListener(
        "submit",
        saveAirport
    );


    // Airport Select

    document.getElementById(
        "airportSelect"
    ).addEventListener(
        "change",
        async function () {

            selectedAirportId =
                this.value
                    ? Number(this.value)
                    : null;

            await handleAirportSelection();

        }
    );


    // Edit Airport

    document.getElementById(
        "editAirportBtn"
    ).addEventListener(
        "click",
        function () {

            if (selectedAirportId) {

                editAirport(
                    selectedAirportId
                );

            }

        }
    );


    // Delete Airport

    document.getElementById(
        "deleteAirportBtn"
    ).addEventListener(
        "click",
        function () {

            if (selectedAirportId) {

                deleteAirport(
                    selectedAirportId
                );

            }

        }
    );


    // Resource modal

    document.getElementById(
        "closeResourceModal"
    ).addEventListener(
        "click",
        closeResourceModal
    );


    document.getElementById(
        "cancelResource"
    ).addEventListener(
        "click",
        closeResourceModal
    );


    document.getElementById(
        "resourceForm"
    ).addEventListener(
        "submit",
        saveResource
    );


    // Resource buttons

    document.getElementById(
        "addTerminalBtn"
    ).addEventListener(
        "click",
        function () {

            openResourceModal(
                "terminal"
            );

        }
    );


    document.getElementById(
        "addGateBtn"
    ).addEventListener(
        "click",
        function () {

            openResourceModal(
                "gate"
            );

        }
    );


    document.getElementById(
        "addRunwayBtn"
    ).addEventListener(
        "click",
        function () {

            openResourceModal(
                "runway"
            );

        }
    );


    document.getElementById(
        "addAtcBtn"
    ).addEventListener(
        "click",
        function () {

            openResourceModal(
                "atc"
            );

        }
    );


    document.getElementById(
        "addWeatherBtn"
    ).addEventListener(
        "click",
        function () {

            openResourceModal(
                "weather"
            );

        }
    );


    // Tabs

    document
        .querySelectorAll(
            ".resource-tab"
        )
        .forEach(
            function (tab) {

                tab.addEventListener(
                    "click",
                    function () {

                        switchTab(
                            this.dataset.tab
                        );

                    }
                );

            }
        );

}


// =========================================================
// LOAD AIRPORTS
// =========================================================

async function loadAirports() {

    try {

        const response =
            await fetch(
                "/airports",
                {
                    method: "GET",

                    headers: {
                        "Accept":
                            "application/json"
                    }
                }
            );


        const responseText =
            await response.text();


        console.log(
            "GET /airports:",
            response.status,
            responseText
        );


        let data = {};

        try {

            data =
                responseText
                    ? JSON.parse(
                        responseText
                    )
                    : {};

        } catch (error) {

            throw new Error(
                `Invalid server response. HTTP ${response.status}`
            );

        }


        if (!response.ok) {

            throw new Error(
                data.message
                ||
                data.error
                ||
                "Unable to load airports"
            );

        }


        airports =
            data.airports
            ||
            (
                Array.isArray(data)
                    ? data
                    : []
            );


        renderAirportSelect();


    } catch (error) {

        console.error(
            "LOAD AIRPORTS ERROR:",
            error
        );


        showToast(
            error.message
            ||
            "Unable to load airports",
            "error"
        );

    }

}


// =========================================================
// AIRPORT DROPDOWN
// =========================================================

function renderAirportSelect() {

    const select =
        document.getElementById(
            "airportSelect"
        );


    select.innerHTML = `

        <option value="">
            Select Airport
        </option>

    `;


    airports.forEach(
        function (airport) {

            const option =
                document.createElement(
                    "option"
                );


            option.value =
                airport.airport_id;


            option.textContent =
                `${airport.airport_code}
                - ${airport.airport_name}`;


            select.appendChild(
                option
            );

        }
    );

}


// =========================================================
// AIRPORT SELECTION
// =========================================================

async function handleAirportSelection() {

    const overview =
        document.getElementById(
            "airportOverview"
        );


    const emptyState =
        document.getElementById(
            "noAirportState"
        );


    if (!selectedAirportId) {

        overview.style.display =
            "none";

        emptyState.style.display =
            "block";

        document.getElementById(
            "airportStatus"
        ).textContent =
            "No airport selected";

        return;

    }


    const airport =
        airports.find(
            function (item) {

                return Number(
                    item.airport_id
                )
                ===
                Number(
                    selectedAirportId
                );

            }
        );


    if (!airport) {

        return;

    }


    emptyState.style.display =
        "none";


    overview.style.display =
        "block";


    renderAirportOverview(
        airport
    );


    await loadAirportResources();

}


// =========================================================
// AIRPORT OVERVIEW
// =========================================================

function renderAirportOverview(
    airport
) {

    document.getElementById(
        "selectedAirportName"
    ).textContent =
        airport.airport_name
        || "-";


    document.getElementById(
        "selectedAirportCode"
    ).textContent =
        airport.airport_code
        || "-";


    document.getElementById(
        "airportCity"
    ).textContent =
        airport.city
        || "-";


    document.getElementById(
        "airportCountry"
    ).textContent =
        airport.country
        || "-";


    document.getElementById(
        "airportTimezone"
    ).textContent =
        airport.timezone
        || "-";


    document.getElementById(
        "airportCapacity"
    ).textContent =
        airport.max_aircraft_capacity
        ?? "-";


    document.getElementById(
        "selectedAirportStatus"
    ).textContent =
        airport.status
        || "ACTIVE";


    document.getElementById(
        "airportStatus"
    ).textContent =
        `${airport.airport_code} selected`;

}


// =========================================================
// LOAD ALL RESOURCES
// =========================================================

async function loadAirportResources() {

    if (!selectedAirportId) {

        return;

    }


    await Promise.all([
        loadTerminals(),
        loadGates(),
        loadRunways(),
        loadAtc(),
        loadWeather()
    ]);

}


// =========================================================
// TERMINALS
// =========================================================

async function loadTerminals() {

    try {

        const response =
            await fetch(
                `/terminals?airport_id=${selectedAirportId}`
            );


        const data =
            await response.json();


        const terminals =
            data.terminals
            ||
            (
                Array.isArray(data)
                    ? data
                    : []
            );


        document.getElementById(
            "terminalCount"
        ).textContent =
            terminals.length;


        renderTerminals(
            terminals
        );


    } catch (error) {

        console.error(
            "TERMINAL ERROR:",
            error
        );


        renderError(
            "terminalsTable"
        );

    }

}


// =========================================================
// RENDER TERMINALS
// =========================================================

function renderTerminals(
    terminals
) {

    const container =
        document.getElementById(
            "terminalsTable"
        );


    if (!terminals.length) {

        container.innerHTML =
            emptyResource(
                "No terminals configured."
            );

        return;

    }


    container.innerHTML = `

        <table>

            <thead>

                <tr>

                    <th>Name</th>

                    <th>Type</th>

                    <th>
                        Passenger Capacity
                    </th>

                    <th>Status</th>

                </tr>

            </thead>

            <tbody>

                ${terminals.map(
                    function (terminal) {

                        return `

                            <tr>

                                <td>
                                    <strong>
                                        ${escapeHtml(
                                            terminal.terminal_name
                                        )}
                                    </strong>
                                </td>

                                <td>
                                    ${escapeHtml(
                                        terminal.terminal_type
                                        || "-"
                                    )}
                                </td>

                                <td>
                                    ${
                                        terminal.passenger_capacity
                                        ?? "-"
                                    }
                                </td>

                                <td>
                                    ${statusBadge(
                                        terminal.status
                                    )}
                                </td>

                            </tr>

                        `;

                    }
                ).join("")}

            </tbody>

        </table>

    `;

}


// =========================================================
// GATES
// =========================================================

async function loadGates() {

    try {

        const response =
            await fetch(
                `/gates?airport_id=${selectedAirportId}`
            );


        const data =
            await response.json();


        const gates =
            data.gates
            ||
            (
                Array.isArray(data)
                    ? data
                    : []
            );


        document.getElementById(
            "gateCount"
        ).textContent =
            gates.length;


        renderGates(
            gates
        );


    } catch (error) {

        console.error(
            "GATE ERROR:",
            error
        );


        renderError(
            "gatesTable"
        );

    }

}


// =========================================================
// RENDER GATES
// =========================================================

function renderGates(
    gates
) {

    const container =
        document.getElementById(
            "gatesTable"
        );


    if (!gates.length) {

        container.innerHTML =
            emptyResource(
                "No gates configured."
            );

        return;

    }


    container.innerHTML = `

        <table>

            <thead>

                <tr>

                    <th>Gate</th>

                    <th>Terminal</th>

                    <th>Type</th>

                    <th>Status</th>

                </tr>

            </thead>

            <tbody>

                ${gates.map(
                    function (gate) {

                        return `

                            <tr>

                                <td>
                                    <strong>
                                        ${escapeHtml(
                                            gate.gate_number
                                        )}
                                    </strong>
                                </td>

                                <td>
                                    ${
                                        escapeHtml(
                                            gate.terminal_name
                                            || "-"
                                        )
                                    }
                                </td>

                                <td>
                                    ${
                                        escapeHtml(
                                            gate.gate_type
                                            || "-"
                                        )
                                    }
                                </td>

                                <td>
                                    ${statusBadge(
                                        gate.status
                                    )}
                                </td>

                            </tr>

                        `;

                    }
                ).join("")}

            </tbody>

        </table>

    `;

}


// =========================================================
// RUNWAYS
// =========================================================

async function loadRunways() {

    try {

        const response =
            await fetch(
                `/runways?airport_id=${selectedAirportId}`
            );


        const data =
            await response.json();


        const runways =
            data.runways
            ||
            (
                Array.isArray(data)
                    ? data
                    : []
            );


        document.getElementById(
            "runwayCount"
        ).textContent =
            runways.length;


        renderRunways(
            runways
        );


    } catch (error) {

        console.error(
            "RUNWAY ERROR:",
            error
        );


        renderError(
            "runwaysTable"
        );

    }

}


// =========================================================
// RENDER RUNWAYS
// =========================================================

function renderRunways(
    runways
) {

    const container =
        document.getElementById(
            "runwaysTable"
        );


    if (!runways.length) {

        container.innerHTML =
            emptyResource(
                "No runways configured."
            );

        return;

    }


    container.innerHTML = `

        <table>

            <thead>

                <tr>

                    <th>Runway</th>

                    <th>Length</th>

                    <th>Type</th>

                    <th>Operation</th>

                    <th>ILS</th>

                    <th>Night</th>

                    <th>Status</th>

                </tr>

            </thead>

            <tbody>

                ${runways.map(
                    function (runway) {

                        return `

                            <tr>

                                <td>
                                    <strong>
                                        ${escapeHtml(
                                            runway.runway_code
                                        )}
                                    </strong>
                                </td>

                                <td>
                                    ${
                                        runway.length_meters
                                        ?? "-"
                                    } m
                                </td>

                                <td>
                                    ${
                                        escapeHtml(
                                            runway.runway_type
                                            || "-"
                                        )
                                    }
                                </td>

                                <td>
                                    ${
                                        escapeHtml(
                                            runway.allowed_operation
                                            || "-"
                                        )
                                    }
                                </td>

                                <td>
                                    ${
                                        runway.ils_available
                                        ? "YES"
                                        : "NO"
                                    }
                                </td>

                                <td>
                                    ${
                                        runway.night_operation
                                        ? "YES"
                                        : "NO"
                                    }
                                </td>

                                <td>
                                    ${statusBadge(
                                        runway.status
                                    )}
                                </td>

                            </tr>

                        `;

                    }
                ).join("")}

            </tbody>

        </table>

    `;

}


// =========================================================
// ATC
// =========================================================

async function loadAtc() {

    try {

        const response =
            await fetch(
                `/atc?airport_id=${selectedAirportId}`
            );


        const data =
            await response.json();


        const controllers =
            data.controllers
            ||
            data.atc
            ||
            (
                Array.isArray(data)
                    ? data
                    : []
            );


        document.getElementById(
            "atcCount"
        ).textContent =
            controllers.length;


        renderAtc(
            controllers
        );


    } catch (error) {

        console.error(
            "ATC ERROR:",
            error
        );


        renderError(
            "atcTable"
        );

    }

}


// =========================================================
// RENDER ATC
// =========================================================

function renderAtc(
    controllers
) {

    const container =
        document.getElementById(
            "atcTable"
        );


    if (!controllers.length) {

        container.innerHTML =
            emptyResource(
                "No ATC controllers configured."
            );

        return;

    }


    container.innerHTML = `

        <table>

            <thead>

                <tr>

                    <th>
                        Employee Code
                    </th>

                    <th>
                        Controller
                    </th>

                    <th>
                        Experience
                    </th>

                    <th>
                        Shift
                    </th>

                    <th>
                        Max Flights
                    </th>

                    <th>
                        Status
                    </th>

                </tr>

            </thead>

            <tbody>

                ${controllers.map(
                    function (controller) {

                        return `

                            <tr>

                                <td>
                                    <strong>
                                        ${escapeHtml(
                                            controller.employee_code
                                        )}
                                    </strong>
                                </td>

                                <td>
                                    ${escapeHtml(
                                        controller.controller_name
                                    )}
                                </td>

                                <td>
                                    ${
                                        controller.experience_years
                                        ?? 0
                                    } years
                                </td>

                                <td>
                                    ${
                                        escapeHtml(
                                            controller.shift
                                            || "-"
                                        )
                                    }
                                </td>

                                <td>
                                    ${
                                        controller.max_concurrent_flights
                                        ?? "-"
                                    }
                                </td>

                                <td>
                                    ${statusBadge(
                                        controller.status
                                    )}
                                </td>

                            </tr>

                        `;

                    }
                ).join("")}

            </tbody>

        </table>

    `;

}


// =========================================================
// WEATHER
// =========================================================

async function loadWeather() {

    try {

        const response =
            await fetch(
                `/weather?airport_id=${selectedAirportId}`
            );


        const data =
            await response.json();


        const weather =
            data.weather
            ||
            data.weather_logs
            ||
            (
                Array.isArray(data)
                    ? data
                    : []
            );


        renderWeather(
            weather
        );


    } catch (error) {

        console.error(
            "WEATHER ERROR:",
            error
        );


        renderError(
            "weatherTable"
        );

    }

}


// =========================================================
// RENDER WEATHER
// =========================================================

function renderWeather(
    weather
) {

    const container =
        document.getElementById(
            "weatherTable"
        );


    if (!weather.length) {

        container.innerHTML =
            emptyResource(
                "No weather records available."
            );

        return;

    }


    container.innerHTML = `

        <table>

            <thead>

                <tr>

                    <th>Condition</th>

                    <th>Visibility</th>

                    <th>Wind</th>

                    <th>Temperature</th>

                    <th>Severity</th>

                    <th>Recorded</th>

                </tr>

            </thead>

            <tbody>

                ${weather.map(
                    function (item) {

                        return `

                            <tr>

                                <td>
                                    <strong>
                                        ${escapeHtml(
                                            item.weather_condition
                                        )}
                                    </strong>
                                </td>

                                <td>
                                    ${
                                        item.visibility_km
                                        ?? "-"
                                    } km
                                </td>

                                <td>
                                    ${
                                        item.wind_speed_kmh
                                        ?? "-"
                                    } km/h
                                </td>

                                <td>
                                    ${
                                        item.temperature_c
                                        ?? "-"
                                    } °C
                                </td>

                                <td>
                                    ${statusBadge(
                                        item.severity
                                    )}
                                </td>

                                <td>
                                    ${
                                        item.recorded_at
                                        || "-"
                                    }
                                </td>

                            </tr>

                        `;

                    }
                ).join("")}

            </tbody>

        </table>

    `;

}


// =========================================================
// ADD AIRPORT MODAL
// =========================================================

function openAddAirportModal() {

    editingAirportId =
        null;


    document.getElementById(
        "airportForm"
    ).reset();


    document.getElementById(
        "airportModalTitle"
    ).textContent =
        "Add Airport";


    document.getElementById(
        "airportTimezoneInput"
    ).value =
        "Asia/Kolkata";


    document.getElementById(
        "operatingHoursInput"
    ).value =
        "24 Hours";


    document.getElementById(
        "airportStatusInput"
    ).value =
        "ACTIVE";


    document.getElementById(
        "airportModal"
    ).style.display =
        "flex";

}


// =========================================================
// EDIT AIRPORT
// =========================================================

async function editAirport(
    airportId
) {

    try {

        const response =
            await fetch(
                `/airports/${airportId}`
            );


        const data =
            await response.json();


        const airport =
            data.airport
            ||
            data;


        editingAirportId =
            airportId;


        document.getElementById(
            "airportCode"
        ).value =
            airport.airport_code
            || "";


        document.getElementById(
            "airportName"
        ).value =
            airport.airport_name
            || "";


        document.getElementById(
            "airportCityInput"
        ).value =
            airport.city
            || "";


        document.getElementById(
            "airportCountryInput"
        ).value =
            airport.country
            || "";


        document.getElementById(
            "airportTimezoneInput"
        ).value =
            airport.timezone
            || "Asia/Kolkata";


        document.getElementById(
            "airportCapacityInput"
        ).value =
            airport.max_aircraft_capacity
            ?? "";


        document.getElementById(
            "operatingHoursInput"
        ).value =
            airport.operating_hours
            || "24 Hours";


        document.getElementById(
            "airportStatusInput"
        ).value =
            airport.status
            || "ACTIVE";


        document.getElementById(
            "airportModalTitle"
        ).textContent =
            "Edit Airport";


        document.getElementById(
            "airportModal"
        ).style.display =
            "flex";


    } catch (error) {

        console.error(
            "EDIT AIRPORT ERROR:",
            error
        );


        showToast(
            error.message,
            "error"
        );

    }

}


// =========================================================
// SAVE AIRPORT
// =========================================================

async function saveAirport(
    event
) {

    event.preventDefault();


    console.log(
        "SAVE AIRPORT BUTTON CLICKED"
    );


    const airportCode =
        document.getElementById(
            "airportCode"
        ).value.trim().toUpperCase();


    const airportName =
        document.getElementById(
            "airportName"
        ).value.trim();


    const city =
        document.getElementById(
            "airportCityInput"
        ).value.trim();


    const country =
        document.getElementById(
            "airportCountryInput"
        ).value.trim();


    const timezone =
        document.getElementById(
            "airportTimezoneInput"
        ).value.trim();


    const capacityValue =
        document.getElementById(
            "airportCapacityInput"
        ).value.trim();


    const operatingHours =
        document.getElementById(
            "operatingHoursInput"
        ).value.trim();


    const status =
        document.getElementById(
            "airportStatusInput"
        ).value;


    // =====================================================
    // VALIDATION
    // =====================================================

    if (!airportCode) {

        showToast(
            "Airport code is required",
            "error"
        );

        return;

    }


    if (!airportName) {

        showToast(
            "Airport name is required",
            "error"
        );

        return;

    }


    if (!city) {

        showToast(
            "City is required",
            "error"
        );

        return;

    }


    if (!country) {

        showToast(
            "Country is required",
            "error"
        );

        return;

    }


    // =====================================================
    // REQUEST DATA
    // =====================================================

    const data = {

        airport_code:
            airportCode,

        airport_name:
            airportName,

        city:
            city,

        country:
            country,

        timezone:
            timezone
            || "Asia/Kolkata",

        max_aircraft_capacity:
            capacityValue
                ? Number(
                    capacityValue
                )
                : null,

        operating_hours:
            operatingHours
            || "24 Hours",

        status:
            status
            || "ACTIVE"

    };


    console.log(
        "AIRPORT DATA:",
        data
    );


    try {

        // =================================================
        // URL + METHOD
        // =================================================

        const url =
            editingAirportId
                ? `/airports/${editingAirportId}`
                : "/airports";


        const method =
            editingAirportId
                ? "PUT"
                : "POST";


        console.log(
            "REQUEST:",
            method,
            url
        );


        // =================================================
        // SEND REQUEST
        // =================================================

        const response =
            await fetch(
                url,
                {

                    method:
                        method,

                    headers: {

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            data
                        )

                }
            );


        console.log(
            "HTTP STATUS:",
            response.status
        );


        // =================================================
        // READ RESPONSE
        // =================================================

        const responseText =
            await response.text();


        console.log(
            "SERVER RESPONSE:",
            responseText
        );


        let result = {};


        try {

            result =
                responseText
                    ? JSON.parse(
                        responseText
                    )
                    : {};

        } catch (jsonError) {

            console.error(
                "JSON PARSE ERROR:",
                jsonError
            );


            throw new Error(
                `Server returned invalid response. HTTP ${response.status}`
            );

        }


        // =================================================
        // SERVER ERROR
        // =================================================

        if (!response.ok) {

            throw new Error(

                result.message
                ||
                result.error
                ||
                `Unable to save airport. HTTP ${response.status}`

            );

        }


        // =================================================
        // SUCCESS
        // =================================================

        console.log(
            "AIRPORT SAVED:",
            result
        );


        showToast(
            editingAirportId
                ? "Airport updated successfully"
                : "Airport created successfully",
            "success"
        );


        closeAirportModal();


        // =================================================
        // RELOAD AIRPORTS
        // =================================================

        await loadAirports();


        // =================================================
        // FIND NEW AIRPORT ID
        // =================================================

        if (
            result.airport_id
        ) {

            selectedAirportId =
                Number(
                    result.airport_id
                );

        }
        else if (
            result.airport
            &&
            result.airport.airport_id
        ) {

            selectedAirportId =
                Number(
                    result.airport.airport_id
                );

        }
        else if (
            editingAirportId
        ) {

            selectedAirportId =
                Number(
                    editingAirportId
                );

        }
        else {

            // If backend doesn't return ID,
            // find airport by code.

            const newAirport =
                airports.find(
                    function (airport) {

                        return (

                            airport.airport_code
                            ===
                            airportCode

                        );

                    }
                );


            if (
                newAirport
            ) {

                selectedAirportId =
                    Number(
                        newAirport.airport_id
                    );

            }

        }


        // =================================================
        // SELECT AIRPORT IN DROPDOWN
        // =================================================

        renderAirportSelect();


        document.getElementById(
            "airportSelect"
        ).value =
            selectedAirportId
            || "";


        // =================================================
        // LOAD AIRPORT
        // =================================================

        await handleAirportSelection();


    } catch (error) {

        console.error(
            "SAVE AIRPORT ERROR:",
            error
        );


        showToast(
            error.message
            ||
            "Unable to save airport",
            "error"
        );

    }

}


// =========================================================
// DELETE AIRPORT
// =========================================================

async function deleteAirport(
    airportId
) {

    const confirmed =
        confirm(
            "Deleting an airport may affect its terminals, gates, runways and flights. Continue?"
        );


    if (!confirmed) {

        return;

    }


    try {

        const response =
            await fetch(
                `/airports/${airportId}`,
                {
                    method: "DELETE"
                }
            );


        const responseText =
            await response.text();


        let data = {};

        try {

            data =
                responseText
                    ? JSON.parse(
                        responseText
                    )
                    : {};

        } catch (error) {

            throw new Error(
                `Invalid server response. HTTP ${response.status}`
            );

        }


        if (!response.ok) {

            throw new Error(
                data.message
                ||
                data.error
                ||
                "Unable to delete airport"
            );

        }


        showToast(
            "Airport deleted successfully",
            "success"
        );


        selectedAirportId =
            null;


        await loadAirports();


        document.getElementById(
            "airportSelect"
        ).value =
            "";


        await handleAirportSelection();


    } catch (error) {

        console.error(
            "DELETE AIRPORT ERROR:",
            error
        );


        showToast(
            error.message,
            "error"
        );

    }

}


// =========================================================
// RESOURCE MODAL
// =========================================================

function openResourceModal(
    type
) {

    if (!selectedAirportId) {

        showToast(
            "Please select an airport first",
            "error"
        );

        return;

    }


    currentResourceType =
        type;


    const titles = {

        terminal:
            "Add Terminal",

        gate:
            "Add Gate",

        runway:
            "Add Runway",

        atc:
            "Add ATC Controller",

        weather:
            "Add Weather"

    };


    document.getElementById(
        "resourceModalTitle"
    ).textContent =
        titles[type];


    document.getElementById(
        "resourceFormContent"
    ).innerHTML =
        getResourceForm(
            type
        );


    document.getElementById(
        "resourceModal"
    ).style.display =
        "flex";


    if (
        type === "gate"
    ) {

        loadTerminalOptions();

    }

}


// =========================================================
// RESOURCE FORMS
// =========================================================

function getResourceForm(
    type
) {

    if (
        type === "terminal"
    ) {

        return `

            <div class="form-grid">

                <div class="form-group">

                    <label>
                        Terminal Name *
                    </label>

                    <input
                        name="terminal_name"
                        class="form-control"
                        placeholder="Terminal 1"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Terminal Type
                    </label>

                    <select
                        name="terminal_type"
                        class="form-control"
                    >

                        <option value="DOMESTIC">
                            DOMESTIC
                        </option>

                        <option value="INTERNATIONAL">
                            INTERNATIONAL
                        </option>

                        <option value="MIXED">
                            MIXED
                        </option>

                    </select>

                </div>


                <div class="form-group">

                    <label>
                        Passenger Capacity
                    </label>

                    <input
                        type="number"
                        name="passenger_capacity"
                        class="form-control"
                        min="0"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Status
                    </label>

                    <select
                        name="status"
                        class="form-control"
                    >

                        <option value="ACTIVE">
                            ACTIVE
                        </option>

                        <option value="INACTIVE">
                            INACTIVE
                        </option>

                    </select>

                </div>

            </div>

        `;

    }


    if (
        type === "gate"
    ) {

        return `

            <div class="form-grid">

                <div class="form-group">

                    <label>
                        Terminal *
                    </label>

                    <select
                        name="terminal_id"
                        id="resourceTerminalSelect"
                        class="form-control"
                        required
                    >

                        <option value="">
                            Loading terminals...
                        </option>

                    </select>

                </div>


                <div class="form-group">

                    <label>
                        Gate Number *
                    </label>

                    <input
                        name="gate_number"
                        class="form-control"
                        placeholder="A01"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Gate Type
                    </label>

                    <input
                        name="gate_type"
                        class="form-control"
                        placeholder="DOMESTIC"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Status
                    </label>

                    <select
                        name="status"
                        class="form-control"
                    >

                        <option value="AVAILABLE">
                            AVAILABLE
                        </option>

                        <option value="OCCUPIED">
                            OCCUPIED
                        </option>

                        <option value="MAINTENANCE">
                            MAINTENANCE
                        </option>

                    </select>

                </div>

            </div>

        `;

    }


    if (
        type === "runway"
    ) {

        return `

            <div class="form-grid">

                <div class="form-group">

                    <label>
                        Runway Code *
                    </label>

                    <input
                        name="runway_code"
                        class="form-control"
                        placeholder="09/27"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Runway Type
                    </label>

                    <select
                        name="runway_type"
                        class="form-control"
                    >

                        <option value="LIGHT">
                            LIGHT
                        </option>

                        <option value="MEDIUM">
                            MEDIUM
                        </option>

                        <option value="HEAVY">
                            HEAVY
                        </option>

                    </select>

                </div>


                <div class="form-group">

                    <label>
                        Length (meters)
                    </label>

                    <input
                        type="number"
                        name="length_meters"
                        class="form-control"
                        min="1"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Width (meters)
                    </label>

                    <input
                        type="number"
                        name="width_meters"
                        class="form-control"
                        min="1"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Allowed Operation
                    </label>

                    <select
                        name="allowed_operation"
                        class="form-control"
                    >

                        <option value="BOTH">
                            BOTH
                        </option>

                        <option value="LANDING">
                            LANDING
                        </option>

                        <option value="TAKEOFF">
                            TAKEOFF
                        </option>

                    </select>

                </div>


                <div class="form-group">

                    <label>
                        Status
                    </label>

                    <select
                        name="status"
                        class="form-control"
                    >

                        <option value="AVAILABLE">
                            AVAILABLE
                        </option>

                        <option value="CLOSED">
                            CLOSED
                        </option>

                        <option value="MAINTENANCE">
                            MAINTENANCE
                        </option>

                    </select>

                </div>


                <div class="form-group">

                    <label>
                        ILS Available
                    </label>

                    <select
                        name="ils_available"
                        class="form-control"
                    >

                        <option value="1">
                            YES
                        </option>

                        <option value="0">
                            NO
                        </option>

                    </select>

                </div>


                <div class="form-group">

                    <label>
                        Night Operation
                    </label>

                    <select
                        name="night_operation"
                        class="form-control"
                    >

                        <option value="1">
                            YES
                        </option>

                        <option value="0">
                            NO
                        </option>

                    </select>

                </div>

            </div>

        `;

    }


    if (
        type === "atc"
    ) {

        return `

            <div class="form-grid">

                <div class="form-group">

                    <label>
                        Employee Code *
                    </label>

                    <input
                        name="employee_code"
                        class="form-control"
                        placeholder="ATC-001"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Controller Name *
                    </label>

                    <input
                        name="controller_name"
                        class="form-control"
                        placeholder="Rahul Sharma"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Experience (Years)
                    </label>

                    <input
                        type="number"
                        name="experience_years"
                        class="form-control"
                        min="0"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Shift
                    </label>

                    <select
                        name="shift"
                        class="form-control"
                    >

                        <option value="MORNING">
                            MORNING
                        </option>

                        <option value="EVENING">
                            EVENING
                        </option>

                        <option value="NIGHT">
                            NIGHT
                        </option>

                    </select>

                </div>


                <div class="form-group">

                    <label>
                        Max Concurrent Flights
                    </label>

                    <input
                        type="number"
                        name="max_concurrent_flights"
                        class="form-control"
                        min="1"
                        value="5"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Status
                    </label>

                    <select
                        name="status"
                        class="form-control"
                    >

                        <option value="AVAILABLE">
                            AVAILABLE
                        </option>

                        <option value="BUSY">
                            BUSY
                        </option>

                        <option value="OFFLINE">
                            OFFLINE
                        </option>

                    </select>

                </div>

            </div>

        `;

    }


    if (
        type === "weather"
    ) {

        return `

            <div class="form-grid">

                <div class="form-group">

                    <label>
                        Weather Condition *
                    </label>

                    <input
                        name="weather_condition"
                        class="form-control"
                        placeholder="Clear"
                        required
                    >

                </div>


                <div class="form-group">

                    <label>
                        Visibility (km)
                    </label>

                    <input
                        type="number"
                        step="0.1"
                        name="visibility_km"
                        class="form-control"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Wind Speed (km/h)
                    </label>

                    <input
                        type="number"
                        name="wind_speed_kmh"
                        class="form-control"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Wind Direction
                    </label>

                    <input
                        type="number"
                        name="wind_direction"
                        class="form-control"
                        placeholder="270"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Temperature (°C)
                    </label>

                    <input
                        type="number"
                        step="0.1"
                        name="temperature_c"
                        class="form-control"
                    >

                </div>


                <div class="form-group">

                    <label>
                        Severity
                    </label>

                    <select
                        name="severity"
                        class="form-control"
                    >

                        <option value="LOW">
                            LOW
                        </option>

                        <option value="MODERATE">
                            MODERATE
                        </option>

                        <option value="HIGH">
                            HIGH
                        </option>

                    </select>

                </div>

            </div>

        `;

    }


    return "";

}


// =========================================================
// LOAD TERMINAL OPTIONS
// =========================================================

async function loadTerminalOptions() {

    try {

        const response =
            await fetch(
                `/terminals?airport_id=${selectedAirportId}`
            );


        const data =
            await response.json();


        const terminals =
            data.terminals
            ||
            (
                Array.isArray(data)
                    ? data
                    : []
            );


        const select =
            document.getElementById(
                "resourceTerminalSelect"
            );


        if (!select) {

            return;

        }


        select.innerHTML = `

            <option value="">
                Select Terminal
            </option>

        `;


        terminals.forEach(
            function (terminal) {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    terminal.terminal_id;


                option.textContent =
                    terminal.terminal_name;


                select.appendChild(
                    option
                );

            }
        );


    } catch (error) {

        console.error(
            "LOAD TERMINALS ERROR:",
            error
        );

    }

}


// =========================================================
// SAVE RESOURCE
// =========================================================

async function saveResource(
    event
) {

    event.preventDefault();


    if (!selectedAirportId) {

        showToast(
            "Please select an airport first",
            "error"
        );

        return;

    }


    const form =
        document.getElementById(
            "resourceForm"
        );


    const formData =
        new FormData(
            form
        );


    const data = {};


    formData.forEach(
        function (
            value,
            key
        ) {

            if (
                value !== ""
            ) {

                data[key] =
                    value;

            }

        }
    );


    [
        "terminal_id",
        "passenger_capacity",
        "length_meters",
        "width_meters",
        "experience_years",
        "max_concurrent_flights",
        "visibility_km",
        "wind_speed_kmh",
        "wind_direction",
        "temperature_c"
    ].forEach(
        function (field) {

            if (
                data[field]
                !== undefined
            ) {

                data[field] =
                    Number(
                        data[field]
                    );

            }

        }
    );


    if (
        data.ils_available
        !== undefined
    ) {

        data.ils_available =
            data.ils_available === "1";

    }


    if (
        data.night_operation
        !== undefined
    ) {

        data.night_operation =
            data.night_operation === "1";

    }


    data.airport_id =
        Number(
            selectedAirportId
        );


    const endpoints = {

        terminal:
            "/terminals",

        gate:
            "/gates",

        runway:
            "/runways",

        atc:
            "/atc",

        weather:
            "/weather"

    };


    try {

        const response =
            await fetch(
                endpoints[
                    currentResourceType
                ],
                {

                    method:
                        "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            data
                        )

                }
            );


        const responseText =
            await response.text();


        let result = {};

        try {

            result =
                responseText
                    ? JSON.parse(
                        responseText
                    )
                    : {};

        } catch (error) {

            throw new Error(
                `Invalid server response. HTTP ${response.status}`
            );

        }


        if (!response.ok) {

            throw new Error(
                result.message
                ||
                result.error
                ||
                "Unable to save resource"
            );

        }


        showToast(
            `${capitalize(
                currentResourceType
            )} added successfully`,
            "success"
        );


        closeResourceModal();


        await loadAirportResources();


    } catch (error) {

        console.error(
            "SAVE RESOURCE ERROR:",
            error
        );


        showToast(
            error.message,
            "error"
        );

    }

}


// =========================================================
// TABS
// =========================================================

function switchTab(
    tab
) {

    document
        .querySelectorAll(
            ".resource-tab"
        )
        .forEach(
            function (item) {

                item.classList.toggle(
                    "active",
                    item.dataset.tab
                    ===
                    tab
                );

            }
        );


    document
        .querySelectorAll(
            ".resource-panel"
        )
        .forEach(
            function (panel) {

                panel.classList.remove(
                    "active"
                );

            }
        );


    const target =
        document.getElementById(
            `${tab}Tab`
        );


    if (target) {

        target.classList.add(
            "active"
        );

    }

}


// =========================================================
// CLOSE MODALS
// =========================================================

function closeAirportModal() {

    document.getElementById(
        "airportModal"
    ).style.display =
        "none";

}


function closeResourceModal() {

    document.getElementById(
        "resourceModal"
    ).style.display =
        "none";

}


// =========================================================
// HELPERS
// =========================================================

function statusBadge(
    status
) {

    const value =
        (
            status
            ||
            "UNKNOWN"
        ).toUpperCase();


    let className =
        "badge-info";


    if (
        value === "ACTIVE"
        ||
        value === "AVAILABLE"
        ||
        value === "LOW"
    ) {

        className =
            "badge-success";

    }


    if (
        value === "HIGH"
        ||
        value === "OFFLINE"
        ||
        value === "CLOSED"
    ) {

        className =
            "badge-danger";

    }


    if (
        value === "MODERATE"
        ||
        value === "BUSY"
        ||
        value === "MAINTENANCE"
    ) {

        className =
            "badge-warning";

    }


    return `

        <span class="badge ${className}">

            ${escapeHtml(value)}

        </span>

    `;

}


function emptyResource(
    message
) {

    return `

        <div class="empty-state">

            ${escapeHtml(
                message
            )}

        </div>

    `;

}


function renderError(
    id
) {

    document.getElementById(
        id
    ).innerHTML = `

        <div class="empty-state">

            Unable to load data.

        </div>

    `;

}


function showToast(
    message,
    type = "success"
) {

    const toast =
        document.getElementById(
            "airportToast"
        );


    if (!toast) {

        console.log(
            message
        );

        return;

    }


    toast.textContent =
        message;


    toast.className =
        `scheduler-toast
         show
         ${type}`;


    setTimeout(
        function () {

            toast.className =
                "scheduler-toast";

        },
        3000
    );

}


function capitalize(
    value
) {

    if (!value) {

        return "";

    }


    return (
        value.charAt(0).toUpperCase()
        +
        value.slice(1)
    );

}


function escapeHtml(
    value
) {

    if (
        value === null
        ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}