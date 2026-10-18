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


document.getElementById(
    "addMatch"
).onclick = function(){


    alert(
        "Открываем добавление матча"
    );


};



document.getElementById(
    "allRatings"
).onclick = function(){


    alert(
        "Открываем все рейтинги"
    );


};






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
      const group = (title, count, list, icon) => `<section class="hero-match-group"><h3>${icon} ${title}<span>${count}</span></h3>${list.length ? list.map(renderMatch).join("") : '<p class="hero-empty">Матчей в этой группе пока нет.</p>'}</section>`;
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
    } catch (error) {
      results.innerHTML = '<p class="hero-empty">Не удалось загрузить отчёт. Проверьте соединение и попробуйте ещё раз.</p>';
    }
  }
})();
