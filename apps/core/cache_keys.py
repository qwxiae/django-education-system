class CacheKeys:
    CATEGORIES        = "categories"
    FEATURED_COURSES  = "featured_courses"

    @staticmethod
    def course(slug):          return f"course:{slug}"
    @staticmethod
    def catalog(category, q):  return f"catalog:{category}:{q}"
    