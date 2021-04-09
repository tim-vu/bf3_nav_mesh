class('Vector')

function Vector.static:DirectionTo(from, to)

  local direction = to - from
  direction:Normalize()

  return direction

end