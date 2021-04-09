NetEvents:Subscribe('Setup:Teleport', function(player, position)

  local soldier = player.soldier

  if not soldier then
    return
  end

  soldier:SetPosition(position)

end)
