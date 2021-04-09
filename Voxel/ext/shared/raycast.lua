require('__shared/vector')

class('Raycast')

function Raycast:__init(from, to, stepSize, maxRaycasts)

  self.from = from
  self.to = to
  self.stepSize = stepSize
  self.maxRaycasts = maxRaycasts

  self.firstDirection = true
  self.position = from

  self.done = false

  self.step = Vector:DirectionTo(from, to)
  self.step = self.step * stepSize

  self.hits = {}

end

function Raycast:performRaycast(performedRaycasts)

  if self.done then
    return true, self.hits
  end

  local raycasts = 0

  if performedRaycasts then
    raycasts = performedRaycasts
  end

  if not self.firstDirection then

    local hit = nil

    while raycasts < self.maxRaycasts do

      hit = RaycastManager:Raycast(self.position, self.from, RayCastFlags.DontCheckCharacter | RayCastFlags.DontCheckWater | RayCastFlags.CheckDetailMesh)

      raycasts = raycasts + 1

      if hit == nil then
        self.done = true
        return true, self.hits
      end

      table.insert(self.hits, hit)

      local newPosition = hit.position - self.step

      --New position lies past from
      if (newPosition - hit.position):Dot(self.from - newPosition) < 0 then
        self.done = true
        return true, self.hits
      end

      self.position = newPosition

    end

    return false
  end

  while raycasts < self.maxRaycasts do

    local hit = RaycastManager:Raycast(self.position, self.to, RayCastFlags.DontCheckCharacter | RayCastFlags.DontCheckPhantoms)

    raycasts = raycasts + 1

    if hit == nil then
      self.firstDirection = false
      self.position = self.to
      return self:performRaycast(raycasts)
    end

    table.insert(self.hits, hit)
    self.position = hit.position + self.step

    local newPosition = hit.position + self.step

    --New position lies past to
    if (newPosition - hit.position):Dot(self.to - newPosition) < 0 then
      self.firstDirection = false
      self.position = self.to
      return self:performRaycast(raycasts)
    end

    self.position = newPosition

  end

  return false
end
