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