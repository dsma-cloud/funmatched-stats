async function loadDashboard(){


// =========================
// Последний матч
// =========================


const match = await fetch(
    "/api/last_match"
)
.then(
    r => r.json()
);



document.getElementById(
    "match"
).innerHTML = `


<div class="match-player">

<b>
${match.player1}
</b>

<br>

⚔️ ${match.hero1}

</div>



<div class="vs">

VS

</div>




<div class="match-player">

<b>
${match.player2}
</b>

<br>

⚔️ ${match.hero2}

</div>




<div class="match-info">

<hr>


🗺 ${match.map}


<div class="winner">

🏆 ${match.winner}

</div>


</div>


`;







// =========================
// Общая статистика
// =========================


const stats = await fetch(
    "/api/stats"
)
.then(
    r => r.json()
);



document.getElementById(
    "stats"
).innerHTML = `


<div class="stat-item">

🎮 Матчи:
<b>${stats.matches}</b>

</div>


<div class="stat-item">

👥 Игроки:
<b>${stats.players}</b>

</div>


<div class="stat-item">

⚔️ Герои:
<b>${stats.heroes}</b>

</div>


<div class="stat-item">

🗺 Поля:
<b>${stats.maps}</b>

</div>


`;







// =========================
// Герои
// =========================


const heroes = await fetch(
    "/api/heroes"
)
.then(
    r => r.json()
);



let heroGroups = {


    meta: [],

    strong: [],

    stable: [],

    other: []

};





function getHeroGroup(winrate){


    let rate = parseFloat(
        winrate.replace(",", ".")
    );



    if(rate >= 75)

        return "meta";



    if(rate >= 60)

        return "strong";



    if(rate >=45)

        return "stable";



    return "other";

}





heroes.forEach(hero => {


    heroGroups[
        getHeroGroup(hero.winrate)
    ].push(hero);


});







function createHeroBlock(
    title,
    list,
    color,
    open=false
){


    if(list.length === 0)

        return "";



    return `


<details class="hero-group ${color}" ${open ? "open" : ""}>


<summary>

${title}

<span>
(${list.length})
</span>


</summary>



<div class="hero-list">


${
list.map(hero=>`


<div class="hero-item">


<b>

${hero.place}. ${hero.hero}

</b>


<br>


🎮 ${hero.games}
&nbsp;|&nbsp;
🏆 ${hero.wins}
&nbsp;|&nbsp;
📊 ${hero.winrate}



</div>


`).join("")
}


</div>


</details>


`;

}



document.getElementById(
    "heroGroups"
).innerHTML =


createHeroBlock(
    "🟡 Мета 75%+",
    heroGroups.meta,
    "meta",
    true
)


+


createHeroBlock(
    "🟢 Сильные 60–75%",
    heroGroups.strong,
    "strong"
)


+


createHeroBlock(
    "🔵 Стабильные 45–60%",
    heroGroups.stable,
    "stable"
)


+


createHeroBlock(
    "⚫ Остальные <45%",
    heroGroups.other,
    "other"
);








// =========================
// Игроки
// =========================


const players = await fetch(
    "/api/players"
)
.then(
    r => r.json()
);



document.getElementById(
    "players"
).innerHTML = players
.slice(0,20)
.map((player,index)=>`


<div class="item">


<div class="rank">

${index + 1}. ${player.player}

</div>



🎮 ${player.games}
&nbsp;|&nbsp;
🏆 ${player.wins}
&nbsp;|&nbsp;
📊 ${player.winrate}



</div>


`)
.join("");









// =========================
// Поля
// =========================


const maps = await fetch(
    "/api/maps"
)
.then(
    r => r.json()
);




document.getElementById(
    "maps"
).innerHTML = maps
.slice(0,20)
.map((map,index)=>`


<div class="item">


<div class="rank">

${index + 1}. ${map.map}

</div>



🎮 ${map.games} игр



</div>


`)
.join("");





}




// =========================
// Кнопки
// =========================


// =========================
// Добавление матча в Google Sheets
// =========================
(function initAddMatchForm() {
  const openButton = document.getElementById("addMatch");
  const modal = document.getElementById("addMatchModal");
  const form = document.getElementById("addMatchForm");
  const message = document.getElementById("addMatchMessage");
  const saveButton = document.getElementById("saveAddMatch");
  const dateInput = document.getElementById("matchDate");
  if (!openButton || !modal || !form) return;

  const closeModal = () => {
    modal.hidden = true;
    message.textContent = "";
    message.className = "add-match-message";
  };

  openButton.addEventListener("click", () => {
    form.reset();
    const today = new Date();
    dateInput.value = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,"0")}-${String(today.getDate()).padStart(2,"0")}`;
    message.textContent = "";
    message.className = "add-match-message";
    modal.hidden = false;
    const firstInput = form.querySelector('input[name="player1"]');
    if (firstInput) firstInput.focus();
  });

  document.getElementById("closeAddMatch").addEventListener("click", closeModal);
  document.getElementById("cancelAddMatch").addEventListener("click", closeModal);
  modal.querySelectorAll("[data-close-add-match]").forEach(el => el.addEventListener("click", closeModal));

  // Подсказки загружаются из справочников Players, Heroes и Maps.
  const lookupTimers = new WeakMap();
  form.querySelectorAll("input[data-lookup]").forEach(input => {
    input.addEventListener("input", () => {
      const query = input.value.trim();
      const list = document.getElementById(input.getAttribute("list"));
      if (!list) return;
      list.replaceChildren();
      if (query.length < 2) return;
      const previousTimer = lookupTimers.get(input);
      if (previousTimer) clearTimeout(previousTimer);
      const timer = setTimeout(async () => {
        try {
          const params = new URLSearchParams({ type: input.dataset.lookup, q: query });
          const response = await fetch(`/api/match_lookup?${params.toString()}`);
          if (!response.ok) return;
          const values = await response.json();
          // Не показываем устаревшие результаты, если пользователь уже продолжил ввод.
          if (input.value.trim() !== query) return;
          list.replaceChildren(...values.map(value => {
            const option = document.createElement("option");
            option.value = value;
            return option;
          }));
        } catch (error) {
          console.error("Не удалось загрузить варианты из справочника:", error);
        }
      }, 180);
      lookupTimers.set(input, timer);
    });
  });

  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = Object.fromEntries(new FormData(form).entries());
    saveButton.disabled = true;
    saveButton.textContent = "Сохраняем…";
    message.textContent = "Отправляем матч в Google Sheets…";
    message.className = "add-match-message";
    try {
      const response = await fetch("/api/matches", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      const result = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(result.error || "Не удалось сохранить матч.");
      message.textContent = "✅ Матч сохранён в таблице Matches.";
      message.className = "add-match-message success";
      form.reset();
      setTimeout(() => {
        closeModal();
        loadDashboard().catch(error => console.error("Не удалось обновить статистику:", error));
        const reportResults = document.getElementById("heroReportResults");
        const reportHero = document.getElementById("heroSearchInput")?.value.trim();
        if (reportHero && reportResults && typeof window.refreshHeroReport === "function") {
          window.refreshHeroReport(reportHero);
        }
      }, 900);
    } catch (error) {
      message.textContent = `❌ ${error.message || "Ошибка сохранения."}`;
      message.className = "add-match-message error";
    } finally {
      saveButton.disabled = false;
      saveButton.textContent = "💾 Сохранить матч";
    }
  });
})();



// Меню раздела «Все отчёты»
(function initReportsMenu() {
  const trigger = document.getElementById("allRatings");
  const menu = document.getElementById("reportsMenu");
  if (!trigger || !menu) return;

  trigger.addEventListener("click", event => {
    event.stopPropagation();
    menu.hidden = !menu.hidden;
    trigger.setAttribute("aria-expanded", String(!menu.hidden));
  });

  menu.addEventListener("click", event => {
    const option = event.target.closest("button[data-open-report]");
    if (!option) return;
    const targetId = option.dataset.openReport;
    document.querySelectorAll("#heroReportSection, #playerReportSection, #heroHeadToHeadSection, #playerHeadToHeadSection, #playerRating7DaysSection, #heroDevelopmentSection, #heroesNotInRatingSection").forEach(section => {
      section.hidden = section.id !== targetId;
    });
    menu.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
    document.getElementById(targetId)?.scrollIntoView({ behavior: "smooth", block: "start" });
    if (targetId === "heroReportSection") document.getElementById("heroSearchInput")?.focus({ preventScroll: true });
    if (targetId === "playerReportSection") document.getElementById("playerSearchInput")?.focus({ preventScroll: true });
    if (targetId === "heroHeadToHeadSection") document.getElementById("headToHeadHero1")?.focus({ preventScroll: true });
    if (targetId === "playerHeadToHeadSection") document.getElementById("headToHeadPlayer1")?.focus({ preventScroll: true });
    if (targetId === "playerRating7DaysSection") loadPlayerRating7Days();
    if (targetId === "heroesNotInRatingSection") loadHeroesNotInRating();
  });

  document.querySelectorAll("[data-close-report]").forEach(button => {
    button.addEventListener("click", () => {
      const section = document.getElementById(button.dataset.closeReport);
      if (section) section.hidden = true;
    });
  });

  document.addEventListener("click", event => {
    if (!event.target.closest(".reports-menu-wrap")) {
      menu.hidden = true;
      trigger.setAttribute("aria-expanded", "false");
    }
  });
})();






loadDashboard();

// =========================
// Отчёт по выбранному герою
// =========================
(function initHeroReport() {
  const input = document.getElementById("heroSearchInput");
  const suggestions = document.getElementById("heroSearchSuggestions");
  const results = document.getElementById("heroReportResults");
  if (!input || !suggestions || !results) return;

  let searchRequest = 0;
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;", "'":"&#39;"}[ch]));

  input.addEventListener("input", async () => {
    const query = input.value.trim();
    const requestId = ++searchRequest;
    if (query.length < 2) { suggestions.hidden = true; suggestions.innerHTML = ""; return; }
    try {
      const response = await fetch(`/api/hero_search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error("Не удалось найти героев");
      const heroes = await response.json();
      if (requestId !== searchRequest) return;
      suggestions.innerHTML = heroes.length
        ? heroes.map(hero => `<button type="button" class="hero-suggestion" data-hero="${escapeHtml(hero)}">${escapeHtml(hero)}</button>`).join("")
        : '<div class="hero-suggestion">Ничего не найдено</div>';
      suggestions.hidden = false;
    } catch (error) {
      suggestions.hidden = true;
      results.innerHTML = '<p class="hero-empty">Не удалось выполнить поиск. Попробуйте ещё раз.</p>';
    }
  });

  suggestions.addEventListener("click", event => {
    const button = event.target.closest("button[data-hero]");
    if (!button) return;
    input.value = button.dataset.hero;
    suggestions.hidden = true;
    loadHeroReport(button.dataset.hero);
  });

  document.addEventListener("click", event => {
    if (!event.target.closest(".hero-search-wrap")) suggestions.hidden = true;
  });

  function renderMatch(match) {
    return `<article class="hero-match-row">
      <div class="hero-match-top"><strong>${escapeHtml(match.date || "Дата не указана")}</strong><span>${escapeHtml(match.map || "Поле не указано")}</span></div>
      <div class="hero-match-vs"><strong>${escapeHtml(match.player1 || "?")}</strong> — ⚔️ ${escapeHtml(match.hero1 || "?")}<br>VS<br><strong>${escapeHtml(match.player2 || "?")}</strong> — ⚔️ ${escapeHtml(match.hero2 || "?")}</div>
      <div class="hero-match-meta">Победитель: ${escapeHtml(match.winner || "не указан")}</div>
    </article>`;
  }

  async function loadHeroReport(hero) {
    results.innerHTML = '<p>Загружаем матчи героя…</p>';
    try {
      const response = await fetch(`/api/hero_report?hero=${encodeURIComponent(hero)}`);
      const report = await response.json();
      if (!response.ok) throw new Error(report.error || "Ошибка загрузки отчёта");
      const stats = report.stats;
      const group = (title, count, list, icon) => `<section class="hero-match-group"><h3>${icon} ${title}<span>${count}</span></h3>${list.length ? `<div class="hero-match-scroll">${list.map(renderMatch).join("")}</div>` : '<p class="hero-empty">Матчей в этой группе пока нет.</p>'}</section>`;
      results.innerHTML = `
        <h3>Статистика: ${escapeHtml(report.hero)}</h3>
        <div class="hero-report-stats">
          <div class="hero-report-stat"><span>Всего матчей</span><strong>${stats.games}</strong></div>
          <div class="hero-report-stat"><span>Победы</span><strong>${stats.wins}</strong></div>
          <div class="hero-report-stat"><span>Поражения</span><strong>${stats.losses}</strong></div>
          <div class="hero-report-stat"><span>Win Rate</span><strong>${String(stats.winrate).replace(".", ",")}%</strong></div>
        </div>
        ${group("Победы героя", stats.wins, report.wins, "🏆")}
        ${group("Поражения героя", stats.losses, report.losses, "❌")}
        ${stats.unresolved ? group("Не удалось определить результат", stats.unresolved, report.unresolved, "❔") : ""}
      `;
      // В карточке героя показываем 3 матча, остальные доступны прокруткой.
      results.querySelectorAll(".hero-match-scroll").forEach(container => {
        const rows = container.querySelectorAll(".hero-match-row");
        if (rows.length > 3) {
          const first = rows[0].getBoundingClientRect().top;
          const third = rows[2].getBoundingClientRect().bottom;
          container.style.maxHeight = `${Math.ceil(third - first + 2)}px`;
          container.style.overflowY = "auto";
          container.style.overscrollBehavior = "contain";
          container.style.paddingRight = "4px";
        }
      });
    } catch (error) {
      results.innerHTML = '<p class="hero-empty">Не удалось загрузить отчёт. Проверьте соединение и попробуйте ещё раз.</p>';
    }
  }
  window.refreshHeroReport = loadHeroReport;
})();


// =========================
// Карточка игрока
// =========================
(function initPlayerReport() {
  const input = document.getElementById("playerSearchInput");
  const suggestions = document.getElementById("playerSearchSuggestions");
  const results = document.getElementById("playerReportResults");
  if (!input || !suggestions || !results) return;

  let searchRequest = 0;
  const escapeHtml = value => String(value ?? "").replace(/[&<>\"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;", "'":"&#39;"}[ch]));

  input.addEventListener("input", async () => {
    const query = input.value.trim();
    const requestId = ++searchRequest;
    if (query.length < 2) { suggestions.hidden = true; suggestions.innerHTML = ""; return; }
    try {
      const response = await fetch(`/api/player_search?q=${encodeURIComponent(query)}`);
      if (!response.ok) throw new Error("Не удалось найти игроков");
      const players = await response.json();
      if (requestId !== searchRequest) return;
      suggestions.innerHTML = players.length
        ? players.map(player => `<button type="button" class="hero-suggestion" data-player="${escapeHtml(player)}">${escapeHtml(player)}</button>`).join("")
        : '<div class="hero-suggestion">Ничего не найдено</div>';
      suggestions.hidden = false;
    } catch (error) {
      suggestions.hidden = true;
      results.innerHTML = '<p class="hero-empty">Не удалось выполнить поиск. Попробуйте ещё раз.</p>';
    }
  });

  suggestions.addEventListener("click", event => {
    const button = event.target.closest("button[data-player]");
    if (!button) return;
    input.value = button.dataset.player;
    suggestions.hidden = true;
    loadPlayerReport(button.dataset.player);
  });

  document.addEventListener("click", event => {
    if (!event.target.closest(".player-search-wrap")) suggestions.hidden = true;
  });

  function renderMatch(match) {
    return `<article class="hero-match-row">
      <div class="hero-match-top"><strong>${escapeHtml(match.date || "Дата не указана")}</strong><span>${escapeHtml(match.map || "Поле не указано")}</span></div>
      <div class="hero-match-vs"><strong>${escapeHtml(match.player1 || "?")}</strong> — ⚔️ ${escapeHtml(match.hero1 || "?")}<br>VS<br><strong>${escapeHtml(match.player2 || "?")}</strong> — ⚔️ ${escapeHtml(match.hero2 || "?")}</div>
      <div class="hero-match-meta">Победитель: ${escapeHtml(match.winner || "не указан")}</div>
    </article>`;
  }

  async function loadPlayerReport(player) {
    results.innerHTML = '<p>Загружаем матчи игрока…</p>';
    try {
      const response = await fetch(`/api/player_report?player=${encodeURIComponent(player)}`);
      const report = await response.json();
      if (!response.ok) throw new Error(report.error || "Ошибка загрузки отчёта");
      const stats = report.stats;
      const group = (title, count, list, icon) => `<section class="hero-match-group"><h3>${icon} ${title}<span>${count}</span></h3>${list.length ? `<div class="player-match-scroll">${list.map(renderMatch).join("")}</div>` : '<p class="hero-empty">Матчей в этой группе пока нет.</p>'}</section>`;
      const favoriteHero = report.favorite_hero ? `${escapeHtml(report.favorite_hero.name)} — ${report.favorite_hero.games} игр` : "Нет данных";
      const favoriteMap = report.favorite_map ? `${escapeHtml(report.favorite_map.name)} — ${report.favorite_map.games} игр` : "Нет данных";
      results.innerHTML = `
        <h3>Статистика: ${escapeHtml(report.player)}</h3>
        <div class="hero-report-stats">
          <div class="hero-report-stat"><span>Всего матчей</span><strong>${stats.games}</strong></div>
          <div class="hero-report-stat"><span>Победы</span><strong>${stats.wins}</strong></div>
          <div class="hero-report-stat"><span>Поражения</span><strong>${stats.losses}</strong></div>
          <div class="hero-report-stat"><span>Win Rate</span><strong>${String(stats.winrate).replace(".", ",")}%</strong></div>
          <div class="hero-report-stat"><span>Чаще всего играл на герое</span><strong>${favoriteHero}</strong></div>
          <div class="hero-report-stat"><span>Чаще всего играл на поле</span><strong>${favoriteMap}</strong></div>
        </div>
        ${group("Победные игры", stats.wins, report.wins, "🏆")}
        ${group("Проигрыши", stats.losses, report.losses, "❌")}
        ${stats.unresolved ? group("Не удалось определить результат", stats.unresolved, report.unresolved, "❔") : ""}
      `;
      // В списках побед и поражений показываем 3 матча, остальные доступны через прокрутку.
      results.querySelectorAll(".player-match-scroll").forEach(container => {
        const rows = container.querySelectorAll(".hero-match-row");
        if (rows.length > 3) {
          const first = rows[0].getBoundingClientRect().top;
          const third = rows[2].getBoundingClientRect().bottom;
          container.style.maxHeight = `${Math.ceil(third - first + 2)}px`;
          container.style.overflowY = "auto";
          container.style.overscrollBehavior = "contain";
          container.style.paddingRight = "4px";
        }
      });
    } catch (error) {
      results.innerHTML = '<p class="hero-empty">Не удалось загрузить карточку игрока. Проверьте соединение и попробуйте ещё раз.</p>';
    }
  }
})();


// =========================
// Противостояние двух героев
// =========================
(function initHeroHeadToHeadReport() {
  const input1 = document.getElementById("headToHeadHero1");
  const input2 = document.getElementById("headToHeadHero2");
  const suggestions1 = document.getElementById("headToHeadHero1Suggestions");
  const suggestions2 = document.getElementById("headToHeadHero2Suggestions");
  const results = document.getElementById("heroHeadToHeadResults");
  if (!input1 || !input2 || !suggestions1 || !suggestions2 || !results) return;

  const escapeHtml = value => String(value ?? "").replace(/[&<>\"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;", "'":"&#39;"}[ch]));
  const state = { hero1: "", hero2: "" };
  const requestIds = { hero1: 0, hero2: 0 };

  function setupSearch(input, suggestions, key) {
    input.addEventListener("input", async () => {
      state[key] = "";
      const query = input.value.trim();
      const requestId = ++requestIds[key];
      if (query.length < 2) { suggestions.hidden = true; suggestions.innerHTML = ""; return; }
      try {
        const response = await fetch(`/api/hero_search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error("Не удалось найти героев");
        const heroes = await response.json();
        if (requestId !== requestIds[key]) return;
        suggestions.innerHTML = heroes.length
          ? heroes.map(hero => `<button type="button" class="hero-suggestion" data-selected-hero="${escapeHtml(hero)}">${escapeHtml(hero)}</button>`).join("")
          : '<div class="hero-suggestion">Ничего не найдено</div>';
        suggestions.hidden = false;
      } catch (_) {
        suggestions.hidden = true;
        results.innerHTML = '<p class="hero-empty">Не удалось выполнить поиск героев. Попробуйте ещё раз.</p>';
      }
    });
    suggestions.addEventListener("click", event => {
      const button = event.target.closest("button[data-selected-hero]");
      if (!button) return;
      state[key] = button.dataset.selectedHero;
      input.value = state[key];
      suggestions.hidden = true;
      if (state.hero1 && state.hero2) loadReport();
    });
  }

  setupSearch(input1, suggestions1, "hero1");
  setupSearch(input2, suggestions2, "hero2");

  document.addEventListener("click", event => {
    if (!event.target.closest("#headToHeadHero1") && !event.target.closest("#headToHeadHero1Suggestions")) suggestions1.hidden = true;
    if (!event.target.closest("#headToHeadHero2") && !event.target.closest("#headToHeadHero2Suggestions")) suggestions2.hidden = true;
  });

  function renderMatch(match) {
    return `<article class="hero-match-row">
      <div class="hero-match-top"><strong>${escapeHtml(match.date || "Дата не указана")}</strong><span>${escapeHtml(match.map || "Поле не указано")}</span></div>
      <div class="hero-match-vs"><strong>${escapeHtml(match.player1 || "?")}</strong> — ⚔️ ${escapeHtml(match.hero1 || "?")}<br>VS<br><strong>${escapeHtml(match.player2 || "?")}</strong> — ⚔️ ${escapeHtml(match.hero2 || "?")}</div>
      <div class="hero-match-meta">Победитель: ${escapeHtml(match.winner || "не указан")} · ${match.result_for_hero1 === "unresolved" ? "Результат не определён" : `${escapeHtml(match.result_for_hero1 === "win" ? match.hero1 : match.hero2)} победил`}</div>
    </article>`;
  }

  async function loadReport() {
    if (state.hero1.toLowerCase() === state.hero2.toLowerCase()) {
      results.innerHTML = '<p class="hero-empty">Выберите двух разных героев.</p>'; return;
    }
    results.innerHTML = '<p>Загружаем игры…</p>';
    try {
      const response = await fetch(`/api/hero_head_to_head?hero1=${encodeURIComponent(state.hero1)}&hero2=${encodeURIComponent(state.hero2)}`);
      const report = await response.json();
      if (!response.ok) throw new Error(report.error || "Ошибка загрузки отчёта");
      const statCard = (hero, stats) => `<div class="hero-report-stat"><span>${escapeHtml(hero)} · Win Rate</span><strong>${String(stats.winrate).replace(".", ",")}%</strong><small>${stats.wins} побед · ${stats.losses} поражений</small></div>`;
      results.innerHTML = `
        <div class="hero-report-stats">
          <div class="hero-report-stat"><span>Всего игр</span><strong>${report.matches.length}</strong><small>${report.stats1.unresolved}</small></div>
          ${statCard(report.hero1, report.stats1)}
          ${statCard(report.hero2, report.stats2)}
        </div>
        <section class="hero-match-group"><h3>Все матчи между героями <span>${report.matches.length}</span></h3>
          ${report.matches.length ? `<div class="hero-head-to-head-scroll">${report.matches.map(renderMatch).join("")}</div>` : '<p class="hero-empty">В таблице Matches пока нет матчей между этими героями.</p>'}
        </section>`;
      // В противостоянии двух героев показываем 3 матча, остальные доступны прокруткой.
      const matchScroll = results.querySelector(".hero-head-to-head-scroll");
      if (matchScroll) {
        const rows = matchScroll.querySelectorAll(".hero-match-row");
        if (rows.length > 3) {
          const first = rows[0].getBoundingClientRect().top;
          const third = rows[2].getBoundingClientRect().bottom;
          matchScroll.style.maxHeight = `${Math.ceil(third - first + 2)}px`;
          matchScroll.style.overflowY = "auto";
          matchScroll.style.overscrollBehavior = "contain";
          matchScroll.style.paddingRight = "4px";
        }
      }
    } catch (error) {
      results.innerHTML = `<p class="hero-empty">${escapeHtml(error.message || "Не удалось загрузить отчёт. Попробуйте ещё раз.")}</p>`;
    }
  }
})();


// =========================
// Противостояние двух игроков
// =========================
(function initPlayerHeadToHeadReport() {
  const input1 = document.getElementById("headToHeadPlayer1");
  const input2 = document.getElementById("headToHeadPlayer2");
  const suggestions1 = document.getElementById("headToHeadPlayer1Suggestions");
  const suggestions2 = document.getElementById("headToHeadPlayer2Suggestions");
  const results = document.getElementById("playerHeadToHeadResults");
  if (!input1 || !input2 || !suggestions1 || !suggestions2 || !results) return;

  const escapeHtml = value => String(value ?? "").replace(/[&<>\"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;", "'":"&#39;"}[ch]));
  const state = { player1: "", player2: "" };
  const requestIds = { player1: 0, player2: 0 };

  function setupSearch(input, suggestions, key) {
    input.addEventListener("input", async () => {
      state[key] = "";
      const query = input.value.trim();
      const requestId = ++requestIds[key];
      if (query.length < 2) { suggestions.hidden = true; suggestions.innerHTML = ""; return; }
      try {
        const response = await fetch(`/api/player_search?q=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error("Не удалось найти игроков");
        const players = await response.json();
        if (requestId !== requestIds[key]) return;
        suggestions.innerHTML = players.length
          ? players.map(player => `<button type="button" class="hero-suggestion" data-selected-player="${escapeHtml(player)}">${escapeHtml(player)}</button>`).join("")
          : '<div class="hero-suggestion">Ничего не найдено</div>';
        suggestions.hidden = false;
      } catch (_) {
        suggestions.hidden = true;
        results.innerHTML = '<p class="hero-empty">Не удалось выполнить поиск игроков. Попробуйте ещё раз.</p>';
      }
    });
    suggestions.addEventListener("click", event => {
      const button = event.target.closest("button[data-selected-player]");
      if (!button) return;
      state[key] = button.dataset.selectedPlayer;
      input.value = state[key];
      suggestions.hidden = true;
      if (state.player1 && state.player2) loadReport();
    });
  }

  setupSearch(input1, suggestions1, "player1");
  setupSearch(input2, suggestions2, "player2");
  document.addEventListener("click", event => {
    if (!event.target.closest("#headToHeadPlayer1") && !event.target.closest("#headToHeadPlayer1Suggestions")) suggestions1.hidden = true;
    if (!event.target.closest("#headToHeadPlayer2") && !event.target.closest("#headToHeadPlayer2Suggestions")) suggestions2.hidden = true;
  });

  function renderMatch(match, result) {
    const resultText = result === "unresolved" ? "Результат не определён" : `${escapeHtml(result === "win" ? state.player1 : state.player2)} победил`;
    return `<article class="hero-match-row">
      <div class="hero-match-top"><strong>${escapeHtml(match.date || "Дата не указана")}</strong><span>${escapeHtml(match.map || "Поле не указано")}</span></div>
      <div class="hero-match-vs"><strong>${escapeHtml(match.player1 || "?")}</strong> — ⚔️ ${escapeHtml(match.hero1 || "?")}<br>VS<br><strong>${escapeHtml(match.player2 || "?")}</strong> — ⚔️ ${escapeHtml(match.hero2 || "?")}</div>
      <div class="hero-match-meta">Победитель: ${escapeHtml(match.winner || "не указан")} · ${resultText}</div>
    </article>`;
  }

  async function loadReport() {
    if (state.player1.toLowerCase() === state.player2.toLowerCase()) {
      results.innerHTML = '<p class="hero-empty">Выберите двух разных игроков.</p>'; return;
    }
    results.innerHTML = '<p>Загружаем игры…</p>';
    try {
      const response = await fetch(`/api/player_head_to_head?player1=${encodeURIComponent(state.player1)}&player2=${encodeURIComponent(state.player2)}`);
      const report = await response.json();
      if (!response.ok) throw new Error(report.error || "Ошибка загрузки отчёта");
      const statCard = (player, stats) => `<div class="hero-report-stat"><span>${escapeHtml(player)} · Win Rate</span><strong>${String(stats.winrate).replace(".", ",")}%</strong><small>${stats.wins} побед · ${stats.losses} поражений</small></div>`;
      results.innerHTML = `
        <div class="hero-report-stats">
          <div class="hero-report-stat"><span>Количество игр</span><strong>${report.matches.length}</strong></div>
          ${statCard(report.player1, report.stats1)}
          ${statCard(report.player2, report.stats2)}
        </div>
        <section class="hero-match-group"><h3>Все матчи между игроками <span>${report.matches.length}</span></h3>
          ${report.matches.length ? report.matches.map(match => renderMatch(match, match.result_for_player1)).join("") : '<p class="hero-empty">В таблице Matches пока нет матчей между этими игроками.</p>'}
        </section>`;
    } catch (error) {
      results.innerHTML = `<p class="hero-empty">${escapeHtml(error.message || "Не удалось загрузить отчёт. Попробуйте ещё раз.")}</p>`;
    }
  }
})();


// =========================
// Рейтинг игроков за последние 7 дней
// =========================
async function loadPlayerRating7Days() {
  const results = document.getElementById("playerRating7DaysResults");
  const period = document.getElementById("playerRating7DaysPeriod");
  if (!results) return;
  results.innerHTML = '<p>Загрузка рейтинга…</p>';
  try {
    const response = await fetch("/api/player_rating_last_7_days");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Не удалось загрузить рейтинг.");
    const formatDate = value => {
      const parts = (value || "").split("-");
      return parts.length === 3 ? `${parts[2]}.${parts[1]}.${parts[0]}` : value;
    };
    if (period) period.textContent = `Период: ${formatDate(data.from)} — ${formatDate(data.to)}. Сначала игроки с большим числом побед; при равенстве учитывается процент побед.`;
    if (!data.players || !data.players.length) {
      results.innerHTML = '<p class="hero-empty">За последние 7 дней матчей не найдено.</p>';
      return;
    }
    const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[char]));
    results.innerHTML = `
      <div style="overflow-x:auto">
        <table style="width:100%;border-collapse:collapse;min-width:420px">
          <thead><tr><th style="text-align:left;padding:10px 8px">#</th><th style="text-align:left;padding:10px 8px">Игрок</th><th style="padding:10px 8px">Игры</th><th style="padding:10px 8px">Победы</th><th style="padding:10px 8px">Поражения</th><th style="padding:10px 8px">% побед</th></tr></thead>
          <tbody>${data.players.map((player, index) => `<tr style="border-top:1px solid #8883"><td style="padding:10px 8px">${index + 1}</td><td style="padding:10px 8px">${escapeHtml(player.player)}</td><td style="text-align:center;padding:10px 8px">${player.games}</td><td style="text-align:center;padding:10px 8px">${player.wins}</td><td style="text-align:center;padding:10px 8px">${player.losses}</td><td style="text-align:center;padding:10px 8px">${player.winrate}%</td></tr>`).join("")}</tbody>
        </table>
      </div>`;
  } catch (error) {
    results.innerHTML = `<p class="hero-empty">${String(error.message || "Ошибка загрузки рейтинга.")}</p>`;
  }
}


async function loadHeroDevelopment() {
  const start = document.getElementById("heroDevelopmentStart")?.value;
  const end = document.getElementById("heroDevelopmentEnd")?.value;
  const results = document.getElementById("heroDevelopmentResults");
  if (!results) return;
  if (!start || !end) { results.innerHTML = '<p class="hero-empty">Укажите обе даты периода.</p>'; return; }
  if (end < start) { results.innerHTML = '<p class="hero-empty">Дата окончания должна быть не раньше даты начала.</p>'; return; }
  results.innerHTML = '<p>Загружаем данные матчей…</p>';
  try {
    const response = await fetch(`/api/hero_development?start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Не удалось загрузить отчёт.");
    const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[char]));
    const fmtDate = value => { const parts = value.split("-"); return `${parts[2]}.${parts[1]}.${parts[0]}`; };
    if (!data.heroes?.length) {
      results.innerHTML = `<p class="hero-empty">За период ${fmtDate(data.from)} — ${fmtDate(data.to)} не найдено героев, перешедших в другую группу рейтинга. Для сравнения нужны матчи с определённым победителем до начала периода и к его окончанию.</p>`;
      return;
    }
    results.innerHTML = `<p class="report-description">Период: ${fmtDate(data.from)} — ${fmtDate(data.to)}. Сравнивается общий винрейт до начала периода и после его окончания.</p><div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;min-width:580px"><thead><tr><th style="text-align:left;padding:10px 8px">Герой</th><th style="text-align:left;padding:10px 8px">Переход</th><th style="padding:10px 8px">Винрейт до</th><th style="padding:10px 8px">Винрейт после</th><th style="padding:10px 8px">Изменение</th><th style="padding:10px 8px">Игры за период</th></tr></thead><tbody>${data.heroes.map(hero => `<tr style="border-top:1px solid #8883"><td style="padding:10px 8px">${escapeHtml(hero.hero)}</td><td style="padding:10px 8px">${escapeHtml(hero.from_group)} → ${escapeHtml(hero.to_group)}</td><td style="text-align:center;padding:10px 8px">${hero.before_winrate}%</td><td style="text-align:center;padding:10px 8px">${hero.after_winrate}%</td><td style="text-align:center;padding:10px 8px">${hero.change > 0 ? "+" : ""}${hero.change} п.п.</td><td style="text-align:center;padding:10px 8px">${hero.period_games} (${hero.period_wins} побед / ${hero.period_losses} поражений)</td></tr>`).join("")}</tbody></table></div>`;
  } catch (error) { results.innerHTML = `<p class="hero-empty">${String(error.message || "Ошибка загрузки отчёта.")}</p>`; }
}

(function initHeroDevelopment() {
  const today = new Date();
  const end = document.getElementById("heroDevelopmentEnd");
  const start = document.getElementById("heroDevelopmentStart");
  const run = document.getElementById("heroDevelopmentRun");
  const toIso = date => `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,"0")}-${String(date.getDate()).padStart(2,"0")}`;
  if (end && start) {
    end.value = toIso(today);
    const first = new Date(today); first.setDate(first.getDate() - 6); start.value = toIso(first);
  }
  run?.addEventListener("click", loadHeroDevelopment);
})();


async function loadHeroesNotInRating() {
  const results = document.getElementById("heroesNotInRatingResults");
  if (!results) return;
  results.innerHTML = '<p>Загружаем список героев…</p>';
  try {
    const response = await fetch("/api/heroes_not_in_rating");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Не удалось загрузить список героев.");
    const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"}[char]));
    if (!data.total) { results.innerHTML = '<p class="hero-empty">Героев с количеством игр меньше 30 не найдено.</p>'; return; }
    results.innerHTML = `<p class="report-description">Всего героев вне рейтинга: ${data.total}. Внутри каждой группы сначала герои с большим количеством игр.</p>${(data.groups || []).map(group => `<details class="unrated-hero-group"><summary>${group.min_games}–${group.max_games} игр <span class="unrated-hero-count">(${group.count} гер.)</span></summary><div class="unrated-hero-list">${group.heroes.length ? group.heroes.map(hero => `<div class="unrated-hero-row"><span>${escapeHtml(hero.hero)}</span><span class="unrated-hero-count">${hero.games} ${hero.games === 1 ? "игра" : hero.games >= 2 && hero.games <= 4 ? "игры" : "игр"}</span></div>`).join("") : '<p class="hero-empty">В этой группе героев нет.</p>'}</div></details>`).join("")}`;
  } catch (error) { results.innerHTML = `<p class="hero-empty">${String(error.message || "Ошибка загрузки списка героев.")}</p>`; }
}
