$(document).ready(function () {

    if (typeof $.cookie("last_menu") === 'undefined'){
        $.cookie("last_menu", ".challenges-sector");
    }

    var menu_option_overview  = $("#menu-option-overview");
    var menu_option_completed = $("#menu-option-completed");
    var menu_option_challenges = $("#menu-option-challenges");
    var menu_option_ranking = $("#menu-option-ranking");

    var overview_sector  = $(".overview-sector");
    var completed_sector  = $(".completed-sector");
    var challenges_sector  = $(".challenges-sector");
    var ranking_sector  = $(".ranking-sector");

    overview_sector.hide(0);
    challenges_sector.hide(0);
    ranking_sector.hide(0);
    completed_sector.hide(0);

    $($.cookie('last_menu')).show();

    menu_option_overview.click(function () {

        if (overview_sector.css('display') !== 'none')
            return;

        var active_section = challenges_sector;

        if (completed_sector.css('display') !== 'none'){
              active_section = completed_sector;
        }
        if (ranking_sector.css('display') !== 'none') {
            active_section = ranking_sector;
        }

        active_section.fadeOut(100, function () {
            active_section.hide();
            overview_sector.fadeIn(100);
            $.cookie("last_menu", ".overview-sector");
        });
    });

    menu_option_challenges.click(function () {

        if (challenges_sector.css('display') !== 'none')
            return;

        var active_section = overview_sector;

        if (completed_sector.css('display') !== 'none'){
              active_section = completed_sector;
        }
        if (ranking_sector.css('display') !== 'none') {
            active_section = ranking_sector;
        }

        active_section.fadeOut(100, function () {
            active_section.hide();
            challenges_sector.fadeIn(100);
            $.cookie("last_menu", ".challenges-sector");
        });
    });

    menu_option_completed.click(function () {

        if (completed_sector.css('display') !== 'none')
            return;

        var active_section = overview_sector;

        if (challenges_sector.css('display') !== 'none') {
            active_section = challenges_sector;
        }
        if (ranking_sector.css('display') !== 'none') {
            active_section = ranking_sector;
        }

        active_section.fadeOut(100, function (){
            active_section.hide();
            completed_sector.fadeIn(100);
        });

        $.cookie("last_menu", ".completed-sector");
    });


    menu_option_ranking.click(function () {

        if (ranking_sector.css('display') !== 'none')
            return;

        var active_section = overview_sector;

        if (challenges_sector.css('display') !== 'none') {
            active_section = challenges_sector;
        }
         if (completed_sector.css('display') !== 'none') {
            active_section = completed_sector;
        }

        active_section.fadeOut(100, function (){
            active_section.hide();
            ranking_sector.fadeIn(100);
        });

        $.cookie("last_menu", ".ranking-sector");
    });

    [].forEach.call($(".challenge-detailed-overview") , function(v,i,a) {
        a.hide(0);
    });

    $(".challenge-overview-button").click(function () {

        if ($("#overview_" + this.id).css('display') !== 'none'){
            $("#overview_" + this.id).fadeOut(100);
            return;
        }

        var revealed = false;

        [].forEach.call($(".challenge-detailed-overview") , function(v,i,a) {
            if (a.css('display') !== 'none')
                //alert(a.css('id') + " fade out");
                a.fadeOut(100, function () {
                    $("#overview_" + this.id).fadeIn(100);
                });
            else
                a.hide(0)
        });

        if (!revealed){
            $("#overview_" + this.id).fadeIn(100);
        }
    });
});