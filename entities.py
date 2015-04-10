import point
import actions
import worldview
import worldmodel

class Background:
   def __init__(self, name, imgs):
      self.name = name
      self.imgs = imgs
      self.current_img = 0


   def get_images(self):
       return self.imgs

   def get_image(self):
       return self.imgs[self.current_img]

   def get_name(self):
       return self.name

   def next_image(self):
       self.current_img = (self.current_img + 1) % len(self.imgs)


class MinerNotFull:
   def __init__(self, name, resource_limit, position, rate, imgs,
      animation_rate):
      self.name = name
      self.position = position
      self.rate = rate
      self.imgs = imgs
      self.current_img = 0
      self.resource_limit = resource_limit
      self.resource_count = 0
      self.animation_rate = animation_rate
      self.pending_actions = []


   def set_position(self, point):
       self.position = point

   def get_position(self):
       return self.position

   def get_images(self):
       return self.imgs

   def get_image(self):
       return self.imgs[self.current_img]

   def get_rate(self):
       return self.rate

   def set_resource_count(self, n):
       self.resource_count = n

   def get_resource_count(self):
       return self.resource_count

   def get_resource_limit(self):
       return self.resource_limit

   def get_name(self):
       return self.name

   def get_animation_rate(self):
       return self.animation_rate

   def remove_pending_action(self, action):
       self.pending_actions.remove(action)

   def add_pending_action(self, action):
       self.pending_actions.append(action)

   def get_pending_actions(self):
      return self.pending_actions

   def clear_pending_actions(self):
      self.pending_actions = []

   def next_image(self):
       self.current_img = (self.current_img + 1) % len(self.imgs)

   def entity_string(self):
       return ' '.join(['miner', self.name, str(self.position.x),
          str(self.position.y), str(self.resource_limit),
          str(self.rate), str(self.animation_rate)])

   def miner_to_ore(self, world, ore):  #minernot full class
       entity_pt = self.get_position()
       if not ore: #am I next to ore??
           return ([entity_pt], False)
       ore_pt = ore.get_position()
       if actions.adjacent(entity_pt, ore_pt):
           self.set_resource_count(1 + self.get_resource_count())
           actions.remove_entity(world, ore)
           return ([ore_pt], True)
       else:
          new_pt = actions.next_position(world, entity_pt, ore_pt)
          return (world.move_entity(self, new_pt), False)


   def create_miner_not_full_action(self, world, i_store): #minernotfull's action
       def action(current_ticks):
           self.remove_pending_action(action)

           entity_pt = self.get_position()
           ore = world.find_nearest(entity_pt, Ore) #find nearest ore
           (tiles, found) = self.miner_to_ore(world, ore) #move to ore

           new_entity = self
           if found:
               new_entity = self.try_transform_miner(world,
                  self.try_transform_miner_not_full)

           actions.schedule_action(world, new_entity,
              self.create_miner_action(world, i_store),
              current_ticks + new_entity.get_rate())
           return tiles
       return action


   def try_transform_miner_not_full(self, world):
       if self.resource_count < self.resource_limit: #carrying fewer than capacity. can only hold 2
           return self
       else:
          new_entity = MinerFull(
              self.get_name(), self.get_resource_limit,
              self.get_position(), self.get_rate(),
              self.get_images(), self.get_animation_rate())
       return new_entity


   def try_transform_miner(self, world, transform): #call function check to see if changed.
       new_entity = transform(world, self)
       if self != new_entity: #did change?
           actions.clear_pending_actions(world, self)
           world.remove_entity_at(self.get_position())
           world.add_entity(new_entity)
           actions.schedule_animation(world, new_entity) #updates world

       return new_entity


   def create_miner_action(self, world, image_store): #into minerfull and minernotfull as 2 separate methods
       if isinstance(self, MinerNotFull):
          return self.create_miner_not_full_action(world, image_store)


   def schedule_miner(self, world, ticks, i_store):
       actions.schedule_action(self, world, self.create_miner_action(world, i_store),
          ticks + self.get_rate())
       actions.schedule_animation(self, world)

   def clear_pending_actions_new(self, world):
       for action in self.get_pending_actions():
           world.unschedule_action(action)
       self.clear_pending_actions()





class MinerFull:
   def __init__(self, name, resource_limit, position, rate, imgs,
      animation_rate):
      self.name = name
      self.position = position
      self.rate = rate
      self.imgs = imgs
      self.current_img = 0
      self.resource_limit = resource_limit
      self.resource_count = resource_limit
      self.animation_rate = animation_rate
      self.pending_actions = []


   def set_position(self, point):
       self.position = point

   def get_position(self):
       return self.position

   def get_images(self):
       return self.imgs

   def get_image(self):
       return self.imgs[self.current_img]

   def get_rate(self):
       return self.rate

   def set_resource_count(self, n):
       self.resource_count = n

   def get_resource_count(self):
       return self.resource_count

   def get_resource_limit(self):
       return self.resource_limit

   def get_name(self):
       return self.name

   def get_animation_rate(self):
       return self.animation_rate

   def remove_pending_action(self, action):
       self.pending_actions.remove(action)

   def add_pending_action(self, action):
       self.pending_actions.append(action)

   def get_pending_actions(self):
      return self.pending_actions

   def clear_pending_actions(self):
      self.pending_actions = []

   def next_image(self):
      self.current_img = (self.current_img + 1) % len(self.imgs)

   def miner_to_smith(self, world, smith): #is the miner next to smith miner full class
       entity_pt = self.get_position()
       if not smith: #am i next to smith
           return ([entity_pt], False)
       smith_pt = smith.get_position()
       if actions.adjacent(entity_pt, smith_pt):
           smith.set_resource_count(
               smith.get_resource_count() +
               self.get_resource_count())
           self.set_resource_count(0)
           return ([], True)
       else:
           new_pt = actions.next_position(world, entity_pt, smith_pt)
           return (world.move_entity(self, new_pt), False)


   def create_miner_full_action(self, world, i_store):
       def action(current_ticks):
          self.remove_pending_action(action)

          entity_pt = self.get_position()
          smith = world.find_nearest(entity_pt, Blacksmith)
          (tiles, found) = self.miner_to_smith(world, smith)

          new_entity = self
          if found:
             new_entity = self.try_transform_miner(world,
                self.try_transform_miner_full)

          actions.schedule_action(world, new_entity,
              new_entity.create_miner_action(world, i_store),
              current_ticks + new_entity.get_rate())
          return tiles
       return action


   def try_transform_miner(self, world, transform): #call function check to see if changed.
       new_entity = transform(world, self)
       if self != new_entity: #did change?
           actions.clear_pending_actions(world, self)
           world.remove_entity_at(self.get_position())
           world.add_entity(new_entity)
           actions.schedule_animation(world, new_entity) #updates world

       return new_entity

   def try_transform_miner_full(self, world): #switched order
       new_entity = MinerNotFull(
           self.get_name(), self.get_resource_limit,
            self.get_position(), self.get_rate(),
            self.get_images(), self.get_animation_rate())

       return new_entity

   def create_miner_action(self, world, image_store): #into minerfull and minernotfull as 2 separate methods
       if isinstance(self, MinerNotFull):
          return self.create_miner_not_full_action(world, image_store)


   def schedule_miner(self, world, ticks, i_store):
       actions.schedule_action(self, world, self.create_miner_action(world, i_store),
          ticks + self.get_rate())
       actions.schedule_animation(self, world)

   def clear_pending_actions_new(self, world):
       for action in self.get_pending_actions():
           world.unschedule_action(action)
       self.clear_pending_actions()




class Vein:
   def __init__(self, name, rate, position, imgs, resource_distance=1):
      self.name = name
      self.position = position
      self.rate = rate
      self.imgs = imgs
      self.current_img = 0
      self.resource_distance = resource_distance
      self.pending_actions = []


   def set_position(self, point):
       self.position = point

   def get_position(self):
       return self.position

   def get_images(self):
       return self.imgs

   def get_image(self):
       return self.imgs[self.current_img]

   def get_rate(self):
       return self.rate

   def get_resource_distance(self):
       return self.resource_distance

   def get_name(self):
       return self.name

   def remove_pending_action(self, action):
       self.pending_actions.remove(action)

   def add_pending_action(self, action):
       self.pending_actions.append(action)

   def get_pending_actions(self):
      return self.pending_actions

   def clear_pending_actions(self):
      self.pending_actions = []

   def next_image(self):
       self.current_img = (self.current_img + 1) % len(self.imgs)

   def entity_string(self):
       return ' '.join(['vein', self.name, str(self.position.x),
         str(self.position.y), str(self.rate),
         str(self.resource_distance)])


   def create_vein_action(self, world, i_store):
       def action(current_ticks):
           self.remove_pending_action(action)

           open_pt = actions.find_open_around(world, self.get_position(),
           self.get_resource_distance())
           if open_pt:
               ore = world.create_ore(
                   "ore - " + self.get_name() + " - " + str(current_ticks),
                    open_pt, current_ticks, i_store)
               world.add_entity(ore)
               tiles = [open_pt]
           else:
               tiles = []

           actions.schedule_action(self, world,
               self.create_vein_action(world, i_store),
               current_ticks + self.get_rate())
           return tiles
       return action


   def schedule_vein(self, world, ticks, i_store):
       actions.schedule_action(self, world, self.create_vein_action(world, i_store),
           ticks + self.get_rate())

class Ore:
   def __init__(self, name, position, imgs, rate=5000):
      self.name = name
      self.position = position
      self.imgs = imgs
      self.current_img = 0
      self.rate = rate
      self.pending_actions = []

   def set_position(self, point):
       self.position = point

   def get_position(self):
       return self.position

   def get_images(self):
       return self.imgs

   def get_image(self):
       return self.imgs[self.current_img]

   def get_rate(self):
       return self.rate

   def get_name(self):
       return self.name

   def remove_pending_action(self, action):
       self.pending_actions.remove(action)

   def add_pending_action(self, action):
       self.pending_actions.append(action)

   def get_pending_actions(self):
      return self.pending_actions

   def clear_pending_actions(self):
      self.pending_actions = []

   def next_image(self):
       self.current_img = (self.current_img + 1) % len(self.imgs)

   def entity_string(self):
       return ' '.join(['ore', self.name, str(self.position.x),
         str(self.position.y), str(self.rate)])


   def create_ore_transform_action(self, world, i_store): #creates blob if ore not collected. place in ore
       def action(current_ticks):
          self.remove_pending_action(action)
          blob = world.create_blob(self.get_name() + " -- blob", #calling create_blob. no blob object place in ore
              self.get_position(),
              self.get_rate() // actions.BLOB_RATE_SCALE,
              current_ticks, i_store)

          actions.remove_entity(self, world)
          world.add_entity(blob)

          return [blob.get_position()]
       return action


   def schedule_ore(self, world, ticks, i_store):
       actions.schedule_action(self, world,
           self.create_ore_transform_action(world, i_store),
           ticks + self.get_rate())


class Blacksmith:
   def __init__(self, name, position, imgs, resource_limit, rate,
      resource_distance=1):
      self.name = name
      self.position = position
      self.imgs = imgs
      self.current_img = 0
      self.resource_limit = resource_limit
      self.resource_count = 0
      self.rate = rate
      self.resource_distance = resource_distance
      self.pending_actions = []

   def set_position(self, point):
       self.position = point

   def get_position(self):
       return self.position

   def get_images(self):
       return self.imgs

   def get_image(self):
       return self.imgs[self.current_img]

   def get_rate(self):
       return self.rate

   def set_resource_count(self, n):
       self.resource_count = n

   def get_resource_count(self):
       return self.resource_count

   def get_resource_limit(self):
       return self.resource_limit

   def get_resource_distance(self):
       return self.resource_distance

   def get_name(self):
       return self.name

   def remove_pending_action(self, action):
       self.pending_actions.remove(action)

   def add_pending_action(self, action):
       self.pending_actions.append(action)

   def get_pending_actions(self):
      return self.pending_actions

   def clear_pending_actions(self):
      self.pending_actions = []

   def next_image(self):
       self.current_img = (self.current_img + 1) % len(self.imgs)

   def entity_string(self):
       return ' '.join(['blacksmith', self.name, str(self.position.x),
         str(self.position.y), str(self.resource_limit),
         str(self.rate), str(self.resource_distance)])

class Obstacle:
   def __init__(self, name, position, imgs):
      self.name = name
      self.position = position
      self.imgs = imgs
      self.current_img = 0

   def set_position(self, point):
       self.position = point

   def get_position(self):
       return self.position

   def get_images(self):
       return self.imgs

   def get_image(self):
       return self.imgs[self.current_img]

   def get_name(self):
       return self.name

   def next_image(self):
       self.current_img = (self.current_img + 1) % len(self.imgs)

   def entity_string(self):
       return ' '.join(['obstacle', self.name, str(self.position.x),
         str(self.position.y)])


class OreBlob:
   def __init__(self, name, position, rate, imgs, animation_rate):
      self.name = name
      self.position = position
      self.rate = rate
      self.imgs = imgs
      self.current_img = 0
      self.animation_rate = animation_rate
      self.pending_actions = []

   def set_position(self, point):
       self.position = point

   def get_position(self):
       return self.position

   def get_images(self):
       return self.imgs

   def get_image(self):
       return self.imgs[self.current_img]

   def get_rate(self):
       return self.rate

   def get_name(self):
       return self.name

   def get_animation_rate(self):
       return self.animation_rate

   def remove_pending_action(self, action):
       self.pending_actions.remove(action)

   def add_pending_action(self, action):
       self.pending_actions.append(action)

   def get_pending_actions(self):
      return self.pending_actions

   def clear_pending_actions(self):
      self.pending_actions = []

   def next_image(self):
       self.current_img = (self.current_img + 1) % len(self.imgs)

   def create_ore_blob_action(self, world, i_store):
       def action(current_ticks):
          self.remove_pending_action(action)

          entity_pt = self.get_position()
          vein = world.find_nearest(entity_pt, Vein)
          (tiles, found) = self.blob_to_vein(world, vein)

          next_time = current_ticks + self.get_rate()
          if found:
              quake = world.create_quake(tiles[0], current_ticks, i_store)
              world.add_entity(quake)
              next_time = current_ticks + self.get_rate() * 2

          actions.schedule_action(self, world,
             self.create_ore_blob_action(world, i_store),
             next_time)

          return tiles
       return action

   def blob_to_vein(self, world, vein): #blob trying to move to vein. nearest vein place in blob
       entity_pt = self.get_position()
       if not vein: #no veins on board
          return ([entity_pt], False)
       vein_pt = vein.get_position()
       if actions.adjacent(entity_pt, vein_pt): #next to vein
           actions.remove_entity(vein, world)
           return ([vein_pt], True)
       else:
          new_pt = actions.blob_next_position(world, entity_pt, vein_pt) #only passing blob's position, place blob_next_position leave as function because works on points and world or miner because function of miner
          old_entity = world.get_tile_occupant(new_pt)
          if isinstance(old_entity, Ore):
             actions.remove_entity(old_entity, world)
       return (world.move_entity(self, new_pt), False)

   def schedule_blob(self, world, ticks, i_store):
       actions.schedule_action(self, world, self.create_ore_blob_action(world, i_store),
          ticks + self.get_rate())
       actions.schedule_animation(self, world)



class Quake:
   def __init__(self, name, position, imgs, animation_rate):
      self.name = name
      self.position = position
      self.imgs = imgs
      self.current_img = 0
      self.animation_rate = animation_rate
      self.pending_actions = []

   def set_position(self, point):
       self.position = point

   def get_position(self):
       return self.position

   def get_images(self):
       return self.imgs

   def get_image(self):
       return self.imgs[self.current_img]

   def get_name(self):
       return self.name

   def get_animation_rate(self):
       return self.animation_rate

   def remove_pending_action(self, action):
       self.pending_actions.remove(action)

   def add_pending_action(self, action):
       self.pending_actions.append(action)

   def get_pending_actions(self):
      return self.pending_actions

   def clear_pending_actions(self):
      self.pending_actions = []

   def next_image(self):
       self.current_img = (self.current_img + 1) % len(self.imgs)


   def create_entity_death_action(self, world):
       def action(current_ticks): #world model schedule an action
          self.remove_pending_action(action)
          pt = self.get_position()
          actions.remove_entity(self, world)
          return [pt]
       return action


   def schedule_quake(self, world, ticks):
       actions.schedule_animation(self, world, actions.QUAKE_STEPS)
       actions.schedule_action(self, world, self.create_entity_death_action(world),
           ticks + actions.QUAKE_DURATION)

   

# This is a less than pleasant file format, but structured based on
# material covered in course.  Something like JSON would be a
# significant improvement.


#def entity_string(entity):
   #if isinstance(entity, MinerNotFull):
      #return ' '.join(['miner', entity.name, str(entity.position.x),
         #str(entity.position.y), str(entity.resource_limit),
         #str(entity.rate), str(entity.animation_rate)])



   #elif isinstance(entity, Vein):
      #return ' '.join(['vein', entity.name, str(entity.position.x),
         #str(entity.position.y), str(entity.rate),
         #str(entity.resource_distance)])



   #elif isinstance(entity, Ore):
      #return ' '.join(['ore', entity.name, str(entity.position.x),
         #str(entity.position.y), str(entity.rate)])


   #elif isinstance(entity, Blacksmith):
      #return ' '.join(['blacksmith', entity.name, str(entity.position.x),
         #str(entity.position.y), str(entity.resource_limit),
         #str(entity.rate), str(entity.resource_distance)])


   #elif isinstance(entity, Obstacle):
      #return ' '.join(['obstacle', entity.name, str(entity.position.x),
         #str(entity.position.y)])
   #else:
      #return 'unknown'
