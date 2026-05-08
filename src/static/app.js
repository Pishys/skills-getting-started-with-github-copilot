document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      console.log("Fetching activities from /activities");
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and activity dropdown
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const participants = details.participants || [];
        const spotsLeft = details.max_participants - participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";

        const participantsHeader = document.createElement("h5");
        participantsHeader.textContent = `Participants (${participants.length})`;
        participantsSection.appendChild(participantsHeader);

        if (participants.length) {
          const participantsList = document.createElement("ul");
          participantsList.className = "participants-list";

          participants.forEach((participant) => {
            const listItem = document.createElement("li");
            listItem.className = "participant-item";

            const participantText = document.createElement("span");
            participantText.textContent = participant;
            listItem.appendChild(participantText);

            const deleteButton = document.createElement("button");
            deleteButton.className = "delete-participant";
            deleteButton.innerHTML = "&#10005;"; // X icon
            deleteButton.title = "Unregister participant";
            deleteButton.addEventListener("click", async () => {
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(participant)}`,
                  {
                    method: "DELETE",
                  }
                );

                const result = await response.json();

                if (response.ok) {
                  messageDiv.textContent = result.message;
                  messageDiv.className = "success";
                  await fetchActivities();
                } else {
                  messageDiv.textContent = result.detail || "An error occurred";
                  messageDiv.className = "error";
                }

                messageDiv.classList.remove("hidden");

                // Hide message after 5 seconds
                setTimeout(() => {
                  messageDiv.classList.add("hidden");
                }, 5000);
              } catch (error) {
                messageDiv.textContent = "Failed to unregister. Please try again.";
                messageDiv.className = "error";
                messageDiv.classList.remove("hidden");
                console.error("Error unregistering:", error);
              }
            });
            listItem.appendChild(deleteButton);

            participantsList.appendChild(listItem);
          });

          participantsSection.appendChild(participantsList);
        } else {
          const noParticipants = document.createElement("p");
          noParticipants.className = "no-participants";
          noParticipants.textContent = "No participants signed up yet.";
          participantsSection.appendChild(noParticipants);
        }

        activityCard.appendChild(participantsSection);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        await fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
