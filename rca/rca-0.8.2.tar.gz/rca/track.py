from dataclasses import dataclass,field

@dataclass
class Track:
  filename: str
  properties: dict
  basename: str = field(init=False)
  ext: str = field(init=False)
  n: int = field(init=False)
  actual_options: str = ''
  desired_options: str = ''
  recode_result: bool = False

  def __post_init__(self):
    elements = self.filename.split('.')
    self.basename = elements[0]
    self.ext = elements[-1]

    # Populate the track number, if it exists (otherwise 0)
    track_num = ''.join([s for s in self.basename if s.isdigit()])
    self.n = 0 if not track_num else int(track_num)

  def apply_properties(self, properties):
    self.properties.update(properties)

  def properties_as_str(self, order):
    values = []
    for key_name in order:
      values.append(self.properties[key_name])
    return ', '.join(values)

