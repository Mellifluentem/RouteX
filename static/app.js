
let monitorStatuses = {};



function renderHistoryChart(checks) {
    const chart = document.getElementById("history-chart");
    const message = document.getElementById("history-chart-message");

    chart.replaceChildren();

    if (checks.length === 0) {
        message.textContent = "No check history available for this monitor.";
        return;
    }

    const orderedChecks = [...checks].reverse();
    const width = Math.max(chart.clientWidth || 600, 320);
    const height = 210;
    const padding = { top: 20, right: 24, bottom: 48, left: 24 };
    const plotWidth = width - padding.left - padding.right;
    const plotHeight = height - padding.top - padding.bottom;
    const timestamps = orderedChecks.map(
        check => new Date(check.checked_at).getTime()
    );

    const validTimes = timestamps.filter(Number.isFinite);
    const minTime = validTimes.length ? Math.min(...validTimes) : 0;
    const maxTime = validTimes.length ? Math.max(...validTimes) : 0;
    const timeRange = maxTime - minTime;

    function getX(index) {
        if (!Number.isFinite(timestamps[index]) || timeRange === 0) {
            return padding.left + plotWidth / 2;
        }

        return padding.left +
            ((timestamps[index] - minTime) / timeRange) * plotWidth;
    }

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label", "Monitor check status history over time");

    function addSvgElement(tag, attributes, textContent) {
        const element = document.createElementNS(svgNS, tag);

        for (const [key, value] of Object.entries(attributes)) {
            element.setAttribute(key, value);
        }

        if (textContent !== undefined) {
            element.textContent = textContent;
        }

        svg.appendChild(element);
        return element;
    }

    const upY = padding.top + 20;
    const downY = padding.top + plotHeight - 20;
    const axisY = height - padding.bottom + 8;

    addSvgElement("text", {
        x: padding.left,
        y: 12,
        fill: "#31d69a",
        "font-size": 11
    }, "UP");

    addSvgElement("text", {
        x: width - padding.right,
        y: height - padding.bottom + 2,
        fill: "#ff6577",
        "font-size": 11,
        "text-anchor": "end"
    }, "DOWN");

    addSvgElement("line", {
        x1: padding.left,
        x2: width - padding.right,
        y1: axisY,
        y2: axisY,
        stroke: "#536078"
    });

    orderedChecks.forEach((check, index) => {
      const x = getX(index);


      const previousCheck = orderedChecks[index - 1];
      const nextCheck = orderedChecks[index + 1];

      const isDown = check.status !== "UP";
      const previousIsDown = previousCheck?.status === "DOWN";
      const nextIsDown = nextCheck?.status === "DOWN";

      if (isDown && (previousIsDown || nextIsDown)) {
          addSvgElement("circle", {
              cx: getX(index),
              cy: downY,
              r: 8,
              fill: "none",
              stroke: "#ff6577",
              "stroke-width": 2,
              opacity: 0.55
          });
      }
        const isUp = check.status === "UP";
        const y = isUp ? upY : downY;

        const point = addSvgElement("circle", {
            cx: x,
            cy: y,
            r: orderedChecks.length > 80 ? 3 : 5,
            fill: isUp ? "#31d69a" : "#ff6577"
        });

        const date = new Date(check.checked_at);
        const timestamp = Number.isNaN(date.getTime())
            ? check.checked_at
            : date.toLocaleString();

        const tooltip = document.createElementNS(svgNS, "title");
        tooltip.textContent =
            `${check.status} — ${timestamp}` +
            (check.latency_ms == null ? "" : ` — ${check.latency_ms} ms`);

        point.appendChild(tooltip);

        // Erişilebilirlik için noktanın açıklaması
        point.setAttribute("tabindex", "0");
        point.setAttribute(
            "aria-label",
            `${check.status}, ${timestamp}` +
            (check.latency_ms == null ? "" : `, ${check.latency_ms} ms`)
        );
    });

    const labelIndexes = [...new Set([
        0,
        Math.floor((orderedChecks.length - 1) / 2),
        orderedChecks.length - 1
    ])];

    for (const index of labelIndexes) {
        const check = orderedChecks[index];
        const date = new Date(check.checked_at);

        const label = Number.isNaN(date.getTime())
            ? String(check.checked_at)
            : date.toLocaleString([], {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            });

        const x = getX(index);

        addSvgElement("text", {
            x,
            y: height - 12,
            fill: "#91a0b8",
            "font-size": 10,
            "text-anchor": index === 0
                ? "start"
                : index === orderedChecks.length - 1
                    ? "end"
                    : "middle"
        }, label);
    }

    chart.appendChild(svg);

    const upCount = orderedChecks.filter(
        check => check.status === "UP"
    ).length;

    message.textContent =
        `${orderedChecks.length} checks · ${upCount} UP · ` +
        `${orderedChecks.length - upCount} DOWN`;
}





async function loadStats(monitorId) {
    const statsSection = document.getElementById("history-stats");
    const chart = document.getElementById("history-chart");
    const chartMessage = document.getElementById("history-chart-message");

    statsSection.hidden = true;
    chart.replaceChildren();
    chartMessage.textContent = "Loading statistics...";

    try {
        const response = await fetch(`/monitors/${monitorId}/stats`);

        if (!response.ok) {
            throw new Error("Could not load monitor statistics.");
        }

        const stats = await response.json();

        document.getElementById("history-total").textContent =
            stats.total_checks;

        document.getElementById("history-success").textContent =
            `${stats.success_rate}%`;

        document.getElementById("history-latency").textContent =
            stats.avg_latency_ms == null
                ? "—"
                : `${stats.avg_latency_ms} ms`;

        statsSection.hidden = false;
        chartMessage.textContent = "";
    } catch (error) {
        chartMessage.textContent = "Could not load monitor statistics.";
        console.error(error);
    }
}


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
  loadStats(monitorId);



    try {
        const response = await fetch(`/monitors/${monitorId}/checks`);

        if (!response.ok) {
            throw new Error("Could not load check history.");
        }


        const data = await response.json();
        const checks = data.checks;

        const downtimeElement = document.getElementById("history-downtime");
        const orderedChecks = [...checks].reverse();

        let downtimeMs = 0;
        let downStartedAt = null;

        for (const check of orderedChecks) {
            const checkedAt = new Date(check.checked_at).getTime();

            if (!Number.isFinite(checkedAt)) {
                continue;
            }

            if (check.status === "DOWN") {
                if (downStartedAt === null) {
                    downStartedAt = checkedAt;
                }
            } else if (check.status === "UP" && downStartedAt !== null) {
                downtimeMs += Math.max(0, checkedAt - downStartedAt);
                downStartedAt = null;
            }
        }

        if (downStartedAt !== null && orderedChecks.length > 0) {
            const lastCheck = new Date(
                orderedChecks[orderedChecks.length - 1].checked_at
            ).getTime();

            if (Number.isFinite(lastCheck)) {
                downtimeMs += Math.max(0, lastCheck - downStartedAt);
            }
        }

        const totalMinutes = Math.floor(downtimeMs / 60000);
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;

        downtimeElement.textContent = hours > 0
            ? `${hours}h ${minutes}m`
            : `${minutes}m`;

        renderHistoryChart(checks);


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
