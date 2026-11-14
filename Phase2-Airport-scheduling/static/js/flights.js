// =========================================
// FLIGHTS MANAGEMENT
// =========================================

let allFlights = [];
let editingFlightId = null;


// =========================================
// DOM
// =========================================

const flightModal =
    document.getElementById(
        "flightModal"
    );

const flightForm =
    document.getElementById(
        "flightForm"
    );


// =========================================
// PAGE LOAD
// =========================================

document.addEventListener(
    "DOMContentLoaded",
    async function () {

        await loadDropdowns();

        await loadFlights();

        setupEvents();

    }
);


// =========================================
// EVENTS
// =========================================

function setupEvents() {

    document.getElementById(
        "openFlightModal"
    ).addEventListener(
        "click",
        openAddModal
    );


    document.getElementById(
        "closeFlightModal"
    ).addEventListener(
        "click",
        closeModal
    );


    document.getElementById(
        "cancelFlight"
    ).addEventListener(
        "click",
        closeModal
    );


    flightForm.addEventListener(
        "submit",
        saveFlight
    );


    document.getElementById(
        "refreshFlights"
    ).addEventListener(
        "click",
        loadFlights
    );


    document.getElementById(
        "filterAirport"
    ).addEventListener(
        "change",
        loadFlights
    );


    document.getElementById(
        "filterStatus"
    ).addEventListener(
        "change",
        filterTable
    );


    document.getElementById(
        "operationType"
    ).addEventListener(
        "change",
        toggleOperationFields
    );


    document.getElementById(
        "currentSituation"
    ).addEventListener(
        "change",
        function () {

            if (
                this.value ===
                "EMERGENCY"
            ) {

                document.getElementById(
                    "isEmergency"
                ).value = "true";

            }

        }
    );

}


// =========================================
// LOAD DROPDOWNS
// =========================================

async function loadDropdowns() {

    try {

        await loadAirports();

        await loadAirlines();

        await loadAircraft();

        await loadTerminals();

        await loadGates();

    } catch (error) {

        console.error(
            error
        );

        showToast(
            "Unable to load form data",
            "error"
        );

    }

}


// =========================================
// AIRPORTS
// =========================================

async function loadAirports() {

    const response =
        await fetch(
            "/airports"
        );

    const data =
        await response.json();

    const airports =
        extractList(
            data,
            "airports"
        );

    const selects = [

        document.getElementById(
            "airportId"
        ),

        document.getElementById(
            "filterAirport"
        )

    ];

    selects.forEach(
        function (select) {

            const firstOption =
                select.options[0]
                    ?.outerHTML
                || "";

            select.innerHTML =
                firstOption;

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
    );

}


// =========================================
// AIRLINES
// =========================================

async function loadAirlines() {

    const response =
        await fetch(
            "/airlines"
        );

    const data =
        await response.json();

    const airlines =
        extractList(
            data,
            "airlines"
        );

    const select =
        document.getElementById(
            "airlineId"
        );

    airlines.forEach(
        function (airline) {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                airline.airline_id;

            option.textContent =
                `${airline.airline_code}
                - ${airline.airline_name}`;

            select.appendChild(
                option
            );

        }
    );

}


// =========================================
// AIRCRAFT
// =========================================

async function loadAircraft() {

    const response =
        await fetch(
            "/aircraft"
        );

    const data =
        await response.json();

    const aircraft =
        extractList(
            data,
            "aircraft"
        );

    const select =
        document.getElementById(
            "aircraftId"
        );

    aircraft.forEach(
        function (item) {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                item.aircraft_id;

            option.textContent =
                `${item.registration_number}
                - ${item.model}`;

            select.appendChild(
                option
            );

        }
    );

}


// =========================================
// TERMINALS
// =========================================

async function loadTerminals() {

    const response =
        await fetch(
            "/terminals"
        );

    const data =
        await response.json();

    const terminals =
        extractList(
            data,
            "terminals"
        );

    const select =
        document.getElementById(
            "terminalId"
        );

    terminals.forEach(
        function (item) {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                item.terminal_id;

            option.textContent =
                item.terminal_name;

            select.appendChild(
                option
            );

        }
    );

}


// =========================================
// GATES
// =========================================

async function loadGates() {

    const response =
        await fetch(
            "/gates"
        );

    const data =
        await response.json();

    const gates =
        extractList(
            data,
            "gates"
        );

    const select =
        document.getElementById(
            "gateId"
        );

    gates.forEach(
        function (item) {

            const option =
                document.createElement(
                    "option"
                );

            option.value =
                item.gate_id;

            option.textContent =
                item.gate_number;

            select.appendChild(
                option
            );

        }
    );

}


// =========================================
// LOAD FLIGHTS
// =========================================

async function loadFlights() {

    try {

        const airportId =
            document.getElementById(
                "filterAirport"
            ).value;

        let url =
            "/flights";

        if (airportId) {

            url +=
                `?airport_id=${airportId}`;

        }

        const response =
            await fetch(
                url
            );

        const data =
            await response.json();

        allFlights =
            data.flights || [];

        renderFlights(
            allFlights
        );

    } catch (error) {

        console.error(
            error
        );

        showToast(
            "Unable to load flights",
            "error"
        );

    }

}


// =========================================
// RENDER FLIGHTS
// =========================================

function renderFlights(
    flights
) {

    const body =
        document.getElementById(
            "flightTableBody"
        );

    const wrapper =
        document.getElementById(
            "flightTableWrapper"
        );

    const loading =
        document.getElementById(
            "flightLoading"
        );

    body.innerHTML =
        "";

    document.getElementById(
        "flightCount"
    ).textContent =
        `${flights.length} Flights`;


    if (!flights.length) {

        wrapper.style.display =
            "none";

        loading.style.display =
            "block";

        loading.textContent =
            "No flights found.";

        return;

    }


    loading.style.display =
        "none";

    wrapper.style.display =
        "block";


    flights.forEach(
        function (flight) {

            const row =
                document.createElement(
                    "tr"
                );

            row.innerHTML = `

                <td>
                    <strong>
                        ${escapeHtml(
                            flight.flight_number
                        )}
                    </strong>

                    <br>

                    <small>
                        ID:
                        ${flight.flight_id}
                    </small>
                </td>

                <td>
                    ${escapeHtml(
                        flight.airline_code
                        || "-"
                    )}

                    <br>

                    <small>
                        ${escapeHtml(
                            flight.airline_name
                            || ""
                        )}
                    </small>
                </td>

                <td>
                    ${escapeHtml(
                        flight.airport_code
                        || "-"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        flight.operation_type
                    )}
                </td>

                <td>
                    ${situationBadge(
                        flight.current_situation
                    )}
                </td>

                <td>
                    ${
                        flight.processing_time_minutes
                        ?? 10
                    } min
                </td>

                <td>
                    ${
                        flight.fuel_percentage
                        ?? "-"
                    }%
                </td>

                <td>
                    ${statusBadge(
                        flight.status
                    )}
                </td>

                <td>

                    <div
                        class="action-buttons"
                    >

                        <button
                            class="action-btn edit-btn"
                            onclick="editFlight(
                                ${flight.flight_id}
                            )"
                        >
                            Edit
                        </button>

                        <button
                            class="action-btn delete-btn"
                            onclick="deleteFlight(
                                ${flight.flight_id}
                            )"
                        >
                            Delete
                        </button>

                    </div>

                </td>

            `;

            body.appendChild(
                row
            );

        }
    );

}


// =========================================
// FILTER
// =========================================

function filterTable() {

    const status =
        document.getElementById(
            "filterStatus"
        ).value;

    if (!status) {

        renderFlights(
            allFlights
        );

        return;

    }

    const filtered =
        allFlights.filter(
            function (flight) {

                return (
                    flight.status
                    === status
                );

            }
        );

    renderFlights(
        filtered
    );

}


// =========================================
// OPEN ADD MODAL
// =========================================

function openAddModal() {

    editingFlightId =
        null;

    flightForm.reset();

    document.getElementById(
        "flightId"
    ).value = "";

    document.getElementById(
        "modalTitle"
    ).textContent =
        "Add Flight";

    document.getElementById(
        "processingTime"
    ).value = 10;

    document.getElementById(
        "priority"
    ).value = 5;

    document.getElementById(
        "currentSituation"
    ).value = "NORMAL";

    flightModal.style.display =
        "flex";

}


// =========================================
// CLOSE MODAL
// =========================================

function closeModal() {

    flightModal.style.display =
        "none";

}


// =========================================
// SAVE FLIGHT
// =========================================

async function saveFlight(
    event
) {

    event.preventDefault();

    const operation =
        document.getElementById(
            "operationType"
        ).value;


    const data = {

        flight_number:
            document.getElementById(
                "flightNumber"
            ).value.trim(),

        airline_id:
            numberValue(
                "airlineId"
            ),

        aircraft_id:
            numberValue(
                "aircraftId"
            ),

        airport_id:
            numberValue(
                "airportId"
            ),

        terminal_id:
            optionalNumber(
                "terminalId"
            ),

        gate_id:
            optionalNumber(
                "gateId"
            ),

        operation_type:
            operation,

        arrival_time:
            operation === "ARRIVAL"
                ? dateValue(
                    "arrivalTime"
                )
                : null,

        departure_time:
            operation === "DEPARTURE"
                ? dateValue(
                    "departureTime"
                )
                : null,

        processing_time_minutes:
            numberValue(
                "processingTime"
            ) || 10,

        priority:
            numberValue(
                "priority"
            ) || 5,

        current_situation:
            document.getElementById(
                "currentSituation"
            ).value,

        fuel_percentage:
            optionalFloat(
                "fuelPercentage"
            ),

        passenger_count:
            optionalNumber(
                "passengerCount"
            ),

        is_emergency:
            document.getElementById(
                "isEmergency"
            ).value === "true",

        emergency_reason:
            document.getElementById(
                "emergencyReason"
            ).value.trim(),

        status:
            "WAITING"

    };


    if (!data.flight_number ||
        !data.airline_id ||
        !data.aircraft_id ||
        !data.airport_id ||
        !data.operation_type
    ) {

        showToast(
            "Please fill all required fields",
            "error"
        );

        return;

    }


    try {

        const id =
            editingFlightId;

        const url =
            id
                ? `/flights/${id}`
                : "/flights";

        const method =
            id
                ? "PUT"
                : "POST";


        const response =
            await fetch(
                url,
                {

                    method,

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify(
                            data
                        )

                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.message
                || "Unable to save flight"
            );

        }


        showToast(
            id
                ? "Flight updated successfully"
                : "Flight created successfully",
            "success"
        );


        closeModal();

        await loadFlights();

    } catch (error) {

        console.error(
            error
        );

        showToast(
            error.message,
            "error"
        );

    }

}


// =========================================
// EDIT FLIGHT
// =========================================

async function editFlight(
    flightId
) {

    try {

        const response =
            await fetch(
                `/flights/${flightId}`
            );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.message
                || "Unable to fetch flight"
            );

        }

        const flight =
            data.flight;


        editingFlightId =
            flightId;


        document.getElementById(
            "modalTitle"
        ).textContent =
            "Edit Flight";


        document.getElementById(
            "flightNumber"
        ).value =
            flight.flight_number
            || "";


        setSelectValue(
            "airlineId",
            flight.airline_id
        );

        setSelectValue(
            "aircraftId",
            flight.aircraft_id
        );

        setSelectValue(
            "airportId",
            flight.airport_id
        );

        setSelectValue(
            "terminalId",
            flight.terminal_id
        );

        setSelectValue(
            "gateId",
            flight.gate_id
        );


        document.getElementById(
            "operationType"
        ).value =
            flight.operation_type
            || "";


        document.getElementById(
            "arrivalTime"
        ).value =
            toDateInput(
                flight.arrival_time
            );


        document.getElementById(
            "departureTime"
        ).value =
            toDateInput(
                flight.departure_time
            );


        document.getElementById(
            "processingTime"
        ).value =
            flight.processing_time_minutes
            ?? 10;


        document.getElementById(
            "priority"
        ).value =
            flight.priority
            ?? 5;


        document.getElementById(
            "currentSituation"
        ).value =
            flight.current_situation
            || "NORMAL";


        document.getElementById(
            "fuelPercentage"
        ).value =
            flight.fuel_percentage
            ?? "";


        document.getElementById(
            "passengerCount"
        ).value =
            flight.passenger_count
            ?? "";


        document.getElementById(
            "isEmergency"
        ).value =
            flight.is_emergency
                ? "true"
                : "false";


        document.getElementById(
            "emergencyReason"
        ).value =
            flight.emergency_reason
            || "";


        toggleOperationFields();


        flightModal.style.display =
            "flex";

    } catch (error) {

        console.error(
            error
        );

        showToast(
            error.message,
            "error"
        );

    }

}


// =========================================
// DELETE FLIGHT
// =========================================

async function deleteFlight(
    flightId
) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this flight?"
        );

    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                `/flights/${flightId}`,
                {
                    method: "DELETE"
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.message
                || "Unable to delete flight"
            );

        }


        showToast(
            "Flight deleted successfully",
            "success"
        );


        await loadFlights();

    } catch (error) {

        console.error(
            error
        );

        showToast(
            error.message,
            "error"
        );

    }

}


// =========================================
// OPERATION FIELDS
// =========================================

function toggleOperationFields() {

    const operation =
        document.getElementById(
            "operationType"
        ).value;


    const arrival =
        document.getElementById(
            "arrivalGroup"
        );

    const departure =
        document.getElementById(
            "departureGroup"
        );


    arrival.style.display =
        operation === "ARRIVAL"
            ? "flex"
            : "none";


    departure.style.display =
        operation === "DEPARTURE"
            ? "flex"
            : "none";

}


// =========================================
// HELPERS
// =========================================

function extractList(
    data,
    key
) {

    if (
        Array.isArray(data)
    ) {

        return data;

    }

    if (
        data &&
        Array.isArray(data[key])
    ) {

        return data[key];

    }

    if (
        data &&
        Array.isArray(data.data)
    ) {

        return data.data;

    }

    return [];

}


function numberValue(
    id
) {

    const value =
        document.getElementById(
            id
        ).value;

    return value
        ? Number(value)
        : null;

}


function optionalNumber(
    id
) {

    const value =
        document.getElementById(
            id
        ).value;

    return value
        ? Number(value)
        : null;

}


function optionalFloat(
    id
) {

    const value =
        document.getElementById(
            id
        ).value;

    return value
        ? Number(value)
        : null;

}


function dateValue(
    id
) {

    const value =
        document.getElementById(
            id
        ).value;

    return value
        ? value.replace(
            "T",
            " "
        ) + ":00"
        : null;

}


function setSelectValue(
    id,
    value
) {

    const select =
        document.getElementById(
            id
        );

    if (value === null ||
        value === undefined
    ) {

        select.value = "";

        return;

    }

    select.value =
        String(value);

}


function toDateInput(
    value
) {

    if (!value) {
        return "";
    }

    if (typeof value === "string") {
        const localDateTime = value.trim().match(
            /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::\d{2}(?:\.\d+)?)?$/
        );

        if (localDateTime) {
            return `${localDateTime[1]}-${localDateTime[2]}-${localDateTime[3]}` +
                `T${localDateTime[4]}:${localDateTime[5]}`;
        }
    }

    const date =
        new Date(value);

    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return String(value)
            .replace(" ", "T")
            .slice(0, 16);

    }

    const pad =
        number =>
            String(number)
                .padStart(2, "0");

    return `${date.getUTCFullYear()}-${pad(
        date.getUTCMonth() + 1
    )}-${pad(
        date.getUTCDate()
    )}T${pad(
        date.getUTCHours()
    )}:${pad(
        date.getUTCMinutes()
    )}`;

}


function situationBadge(
    situation
) {

    const value =
        (
            situation
            || "NORMAL"
        ).toUpperCase();

    let className =
        "badge-info";

    if (
        value === "EMERGENCY" ||
        value === "MEDICAL"
    ) {

        className =
            "badge-danger";

    } else if (
        value === "LOW_FUEL" ||
        value === "WEATHER"
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


function statusBadge(
    status
) {

    const value =
        (
            status
            || "UNKNOWN"
        ).toUpperCase();

    let className =
        "badge-info";

    if (
        value === "WAITING"
    ) {

        className =
            "badge-warning";

    } else if (
        value === "SCHEDULED" ||
        value === "COMPLETED"
    ) {

        className =
            "badge-success";

    } else if (
        value === "EMERGENCY" ||
        value === "CANCELLED"
    ) {

        className =
            "badge-danger";

    }

    return `
        <span class="badge ${className}">
            ${escapeHtml(value)}
        </span>
    `;

}


function escapeHtml(
    value
) {

    if (
        value === null ||
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


function showToast(
    message,
    type = "success"
) {

    const toast =
        document.getElementById(
            "flightToast"
        );

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