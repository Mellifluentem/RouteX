
let monitorStatuses = {};


async function loadHistory(monitorId, monitorName) {
    const historySection = document.getElementById("history-section");
    const historyName = document.getElementById("history-monitor-name");
    const historyMessage = document.getElementById("history-message");
    const historyList = document.getElementById("history-list");

    historySection.hidden = false;
    historyName.textContent = `History for ${monitorName}`;
    historyMessage.textContent = "Loading history...";
    historyList.innerHTML = "";

    historySection.scrollIntoView({ behavior: "smooth" });

    try {
        const response = await fetch(`/monitors/${monitorId}/checks`);

        if (!response.ok) {
            throw new Error("Could not load check history.");
        }

        const data = await response.json();
        const checks = data.checks;

        historyMessage.textContent =
            checks.length === 0 ? "No checks recorded yet." : "";

        for (const check of checks) {
            const row = document.createElement("tr");

            const statusCell = document.createElement("td");
            statusCell.textContent = check.status;
            statusCell.style.color =
                check.status === "UP" ? "#31d69a" : "#ff6577";

            const latencyCell = document.createElement("td");
            latencyCell.textContent =
                check.latency_ms == null
                    ? "—"
                    : `${check.latency_ms} ms`;

            const errorCell = document.createElement("td");
            errorCell.textContent = check.error || "—";

            const timeCell = document.createElement("td");
            const date = new Date(check.checked_at);
            timeCell.textContent = Number.isNaN(date.getTime())
                ? check.checked_at
                : date.toLocaleString();

            row.append(statusCell, latencyCell, errorCell, timeCell);
            historyList.appendChild(row);
        }
    } catch (error) {
        historyMessage.textContent = "Could not load check history.";
        console.error(error);
    }
}


async function loadMonitors() {
    const loadingMessage = document.getElementById("loading-message");
    const monitorList = document.getElementById("monitor-list");

    loadingMessage.textContent = "Loading monitors...";
    monitorList.innerHTML = "";

    try {
        const response = await fetch("/monitors");

        if (!response.ok) {
            throw new Error("Could not load monitors.");
        }

        const data = await response.json();
        const monitors = data.monitors;

        document.getElementById("total-count").textContent =
            monitors.length;

        loadingMessage.textContent =
            monitors.length === 0 ? "No monitors added yet." : "";

        for (const monitor of monitors) {
            const row = document.createElement("tr");

            const nameCell = document.createElement("td");
            nameCell.textContent = monitor.name;

            const targetCell = document.createElement("td");
            targetCell.textContent = monitor.target;

            const typeCell = document.createElement("td");
            typeCell.textContent = monitor.monitor_type.toUpperCase();

            const statusCell = document.createElement("td");
            statusCell.textContent = "Not checked";
            statusCell.style.color = "#91a0b8";

          const actionsCell = document.createElement("td");

          // Enable / Disable button
          const toggleButton = document.createElement("button");
          toggleButton.style.marginLeft = "8px";

          function updateToggleButton() {
              toggleButton.textContent = monitor.enabled ? "Disable" : "Enable";
          }

          updateToggleButton();

          toggleButton.addEventListener("click", async () => {
              toggleButton.disabled = true;

              try {
                  const response = await fetch(
                      `/monitors/${monitor.id}/enabled`,
                      {
                          method: "PATCH",
                          headers: {
                              "Content-Type": "application/json"
                          },
                          body: JSON.stringify({
                              enabled: !monitor.enabled
                          })
                      }
                  );

                  const data = await response.json();

                  if (!response.ok) {
                      throw new Error(
                          data.detail || "Could not update monitor status."
                      );
                  }

                  await loadMonitors();
              } catch (error) {
                  alert(error.message);
                  console.error(error);
              } finally {
                  toggleButton.disabled = false;
              }
          });

          actionsCell.appendChild(toggleButton);

            // Check button
            const checkButton = document.createElement("button");
            checkButton.textContent = "Check";

            checkButton.addEventListener("click", async () => {
                await runCheck(monitor.id, statusCell, checkButton);
            });

          actionsCell.appendChild(checkButton);


          // History button
          const historyButton = document.createElement("button");
          historyButton.textContent = "History";
          historyButton.style.marginLeft = "8px";

          historyButton.addEventListener("click", async () => {
              await loadHistory(monitor.id, monitor.name);
          });

          actionsCell.appendChild(historyButton);


          // Edit button
          const editButton = document.createElement("button");
          editButton.textContent = "Edit";
          editButton.style.marginLeft = "8px";

          editButton.addEventListener("click", () => {
              document.getElementById("edit-monitor-id").value =
                  monitor.id;
              document.getElementById("edit-monitor-name").value =
                  monitor.name;
              document.getElementById("edit-monitor-target").value =
                  monitor.target;
              document.getElementById("edit-monitor-type").value =
                  monitor.monitor_type;
              editMonitorPortInput.value = monitor.port ?? "";

              updateEditMonitorPortVisibility();

            const editSection =
                  document.getElementById("edit-monitor-section");

              editSection.hidden = false;
              editSection.scrollIntoView({ behavior: "smooth" });
          });

          actionsCell.appendChild(editButton);



            // Delete button
            const deleteButton = document.createElement("button");
            deleteButton.textContent = "Delete";
            deleteButton.style.backgroundColor = "#b42335";
            deleteButton.style.marginLeft = "8px";

            deleteButton.addEventListener("click", async () => {
                const confirmed = confirm(
                    `Delete monitor "${monitor.name}"?`
                );

                if (!confirmed) {
                    return;
                }

                deleteButton.disabled = true;
                deleteButton.textContent = "Deleting...";

                try {
                    const deleteResponse = await fetch(
                        `/monitors/${monitor.id}`,
                        { method: "DELETE" }
                    );

                    if (!deleteResponse.ok) {
                        throw new Error("Could not delete monitor.");
                    }

                    delete monitorStatuses[monitor.id];

                    await loadMonitors();
                } catch (error) {
                    alert(error.message);
                    console.error(error);
                } finally {
                    deleteButton.disabled = false;
                    deleteButton.textContent = "Delete";
                }
            });

            actionsCell.appendChild(deleteButton);

            row.append(
                nameCell,
                targetCell,
                typeCell,
                statusCell,
                actionsCell
            );

            monitorList.appendChild(row);
        }

        updateCounters();
    } catch (error) {
        loadingMessage.textContent =
            "Could not connect to the routeX API.";
        console.error(error);
    }
}

function updateCounters() {
    const statuses = Object.values(monitorStatuses);

    const upCount = statuses.filter(
        status => status === "UP"
    ).length;

    const downCount = statuses.filter(
        status => status === "DOWN"
    ).length;

    document.getElementById("up-count").textContent = upCount;
    document.getElementById("down-count").textContent = downCount;
}

async function runCheck(monitorId, statusCell, button) {
    button.disabled = true;
    button.textContent = "Checking...";

    try {
        const response = await fetch(
            `/monitors/${monitorId}/check`,
            { method: "POST" }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Check failed."
            );
        }

        const result = data.check;
        const status = result.status === "UP" ? "UP" : "DOWN";

        monitorStatuses[monitorId] = status;

        statusCell.textContent = status;
        statusCell.style.color =
            status === "UP" ? "#31d69a" : "#ff6577";

        if (result.latency_ms != null) {
            statusCell.textContent += ` (${result.latency_ms} ms)`;
        }

        updateCounters();
    } catch (error) {
        statusCell.textContent = "Error";
        statusCell.style.color = "#ff6577";
        console.error(error);
    } finally {
        button.disabled = false;
        button.textContent = "Check";
    }
}

// TCP port field visibility
const monitorTypeSelect = document.getElementById("monitor-type");
const monitorPortSection = document.getElementById("monitor-port-section");
const monitorPortInput = document.getElementById("monitor-port");

function updateMonitorPortVisibility() {
    const isTcp = monitorTypeSelect.value === "tcp";

    monitorPortSection.hidden = !isTcp;
    monitorPortInput.required = isTcp;

    if (!isTcp) {
        monitorPortInput.value = "";
    }
}

monitorTypeSelect.addEventListener(
    "change",
    updateMonitorPortVisibility
);

updateMonitorPortVisibility();

// Add monitor form
const monitorForm = document.getElementById("monitor-form");

monitorForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const name = document.getElementById("monitor-name").value.trim();
    const target = document.getElementById("monitor-target").value.trim();
    const monitorType = document.getElementById("monitor-type").value;
    const portInput = document.getElementById("monitor-port");
    const port = monitorType === "tcp" ? Number(portInput.value) : null;


    try {
        const response = await fetch("/monitors", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                target: target,
                monitor_type: monitorType,
                ...(monitorType === "tcp" ? { port: port } : {})
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : JSON.stringify(data.detail || "Could not add monitor.")
            );
        }

        monitorForm.reset();
        await loadMonitors();

        alert("Monitor added successfully!");
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error(error);
    }
});


// TCP port field visibility for edit form
const editMonitorTypeSelect =
    document.getElementById("edit-monitor-type");
const editMonitorPortSection =
    document.getElementById("edit-monitor-port-section");
const editMonitorPortInput =
    document.getElementById("edit-monitor-port");

function updateEditMonitorPortVisibility() {
    const isTcp = editMonitorTypeSelect.value === "tcp";

    editMonitorPortSection.hidden = !isTcp;
    editMonitorPortInput.required = isTcp;

    if (!isTcp) {
        editMonitorPortInput.value = "";
    }
}

editMonitorTypeSelect.addEventListener(
    "change",
    updateEditMonitorPortVisibility
);

updateEditMonitorPortVisibility();



const editMonitorForm = document.getElementById("edit-monitor-form");

editMonitorForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const monitorId =
        document.getElementById("edit-monitor-id").value;
    const name =
        document.getElementById("edit-monitor-name").value.trim();
    const target =
        document.getElementById("edit-monitor-target").value.trim();
    const monitorType =
        document.getElementById("edit-monitor-type").value;
    const port = monitorType === "tcp"
        ? Number(editMonitorPortInput.value)
        : null;

  const submitButton =
        editMonitorForm.querySelector('button[type="submit"]');

    submitButton.disabled = true;

    try {
        const response = await fetch(`/monitors/${monitorId}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                target: target,
                monitor_type: monitorType,
                ...(monitorType === "tcp" ? { port: port } : {})
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : JSON.stringify(data.detail || "Could not update monitor.")
            );
        }

        document.getElementById("edit-monitor-section").hidden = true;
        editMonitorForm.reset();

        await loadMonitors();

        alert("Monitor updated successfully!");
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error(error);
    } finally {
        submitButton.disabled = false;
    }
});

document.getElementById("cancel-edit-button").addEventListener("click", () => {
    document.getElementById("edit-monitor-section").hidden = true;
    editMonitorForm.reset();
});

loadMonitors();
