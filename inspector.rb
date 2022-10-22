module Inspector
  def self.filter_inherited_methods(cls)
    raise ArgumentError unless cls.is_a?(Class)

    superclasses = cls.ancestors - [cls]

    superclasses.inject(cls.methods) do |methods, superclass|
      methods - superclass.methods
    end
  end

  def self.module_classes(mod)
    raise ArgumentError unless mod.is_a?(Module)

    mod.constants.select do |const|
      mod.const_get(const).is_a?(Class)
    end
  end
end
