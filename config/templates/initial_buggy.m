Type player_t : 0..1;
Var Players : Array[ player_t ] of Record
                               hasball, gotball: boolean
                             End;

Ruleset p : player_t Do
  Alias ping: Players[p];
        pong: Players[ 1 - p ] Do

    Rule "Get ball"
      ping.gotball
    ==>
    Begin
      ping.hasball := true;
      ping.gotball := false;
    End;

    Rule "Keep ball"
      ping.hasball
    ==>
    Begin
    End;

    Rule "Pass ball"
      ping.hasball
    ==>
    begin
      ping.hasball := false;
      pong.gotball := true;
    End;

    Startstate
    Begin
      ping.hasball := true;
      ping.gotball := false;
      clear pong;
    End;

  End;

End;

Invariant "Only one ball in play."
  Forall p : player_t Do
    !(Players[p].hasball & Players[p].gotball) &
    (Players[p].hasball | Players[p].gotball) ->
    Forall q : player_t Do
      (Players[q].hasball | Players[q].gotball) -> p = q
    End
  End;

Invariant "Player0NeverHasBall"
  !Players[0].hasball;
