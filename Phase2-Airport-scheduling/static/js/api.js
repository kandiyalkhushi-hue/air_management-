// static/js/api.js


async function apiRequest(
    url,
    options = {}
) {

    try {

        const response = await fetch(
            url,
            {
                headers: {
                    "Content-Type":
                        "application/json",

                    ...(options.headers || {})
                },

                ...options
            }
        );

        const data =
            await response.json();

        if (!response.ok) {

            throw new Error(
                data.message ||
                "API request failed"
            );
        }

        return data;

    } catch (error) {

        console.error(
            "API Error:",
            error
        );

        throw error;
    }
}


async function getAirports() {

    return apiRequest(
        "/airports"
    );
}


async function getFlights(
    airportId = null
) {

    let url = "/scheduler/flights";

    if (airportId) {

        url +=
            `?airport_id=${airportId}`;
    }

    return apiRequest(
        url
    );
}


async function getAlgorithms() {

    return apiRequest(
        "/scheduler/algorithms"
    );
}


async function runScheduler(
    airportId,
    algorithm,
    timeQuantum = 3
) {

    return apiRequest(

        `/scheduler/run/${airportId}`,

        {
            method: "POST",

            body: JSON.stringify({

                algorithm:
                    algorithm,

                time_quantum:
                    timeQuantum
            })
        }
    );
}