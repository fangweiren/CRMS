from CRMS.settings import PER_PAGE, SHOW_PAGE


class Pagination(object):
    """自定义分页类"""

    def __init__(self, current_page, total_count, url_prefix):
        """
        :param current_page: 当前页码数
        :param total_count: 数据条数
        :param url_prefix: url 前缀
        """
        self.url_prefix = url_prefix
        # 每一页显示 10 条数据
        self.per_page = PER_PAGE
        # 计算需要多少页
        total_page, more = divmod(total_count, PER_PAGE)
        if more:
            total_page += 1
        self.total_page = total_page

        # 当前页码
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        # 页码必须是大于 0 的数
        current_page = total_page if current_page > total_page else current_page
        if current_page < 1:
            current_page = 1
        self.current_page = current_page
        self.previous = self.current_page - 1
        self.next = self.current_page + 1
        # 页面最多显示的页码数
        self.show_page = SHOW_PAGE
        # 最多显示页码的一半
        self.half_show_page = self.show_page // 2

        self.show_page_list()

    @property
    def start(self):
        """数据切片的开始位置"""
        return (self.current_page - 1) * self.per_page

    @property
    def end(self):
        """"数据切片的结束位置"""
        return self.current_page * self.per_page

    def show_page_list(self):
        # 如果总页码数小于最大要显示的页码数
        if self.total_page < self.show_page:
            show_page_start = 1
            show_page_end = self.total_page
        # 左边越界
        elif self.current_page - self.half_show_page < 1:
            show_page_start = 1
            show_page_end = self.show_page
        # 右边越界
        elif self.current_page + self.half_show_page > self.total_page:
            show_page_end = self.total_page
            show_page_start = self.total_page - self.show_page + 1
        else:
            show_page_start = self.current_page - self.half_show_page
            show_page_end = self.current_page + self.half_show_page

        self.range = range(show_page_start, show_page_end + 1)
