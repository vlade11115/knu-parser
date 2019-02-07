# -*- coding: utf-8 -*-
from scrapy import Spider, http, shell, exceptions

from knu_parser.items import KnuParserItem


class ScheduleSpider(Spider):
    name = 'schedule'
    allowed_domains = ['asu.knu.edu.ua']

    def start_requests(self):
        urls = [
            'http://asu.knu.edu.ua/timeTable/group',
        ]
        for url in urls:
            yield http.FormRequest(url=url, callback=self.parse)

    def parse(self, response):
        """
        Parse initial page, take faculty id and name.
        """
        for faculty in response.xpath('//*[@id="TimeTableForm_faculty"]/option')[1:]:
            faculty_id = faculty.xpath('@value').get()
            if not faculty_id:
                # self.logger.debug('Failed to parse faculty id for %s faculty_id', faculty_id)
                # shell.inspect_response(response, self)
                # raise exceptions.CloseSpider('')
                continue
            faculty_name = faculty.xpath('text()').get()
            item = KnuParserItem()
            form_data = {'TimeTableForm[faculty]': faculty_id}
            item['faculty_id'] = faculty_id
            item['faculty_name'] = faculty_name
            request = http.FormRequest(url=response.url, formdata=form_data, callback=self.parse_course)
            request.meta['item'] = item
            yield request

    def parse_course(self, response):
        """
        Parse id of course.
        """
        for course in response.xpath('//*[@id="TimeTableForm_course"]/option')[1:]:
            course_id = course.xpath('@value').get()
            if not course_id:
                self.logger.debug('Failed to parse id of course for %s course_id', course_id)
                # shell.inspect_response(response, self)
                # raise exceptions.CloseSpider('')
                continue

            item = response.meta['item']
            item['course_id'] = course_id
            form_data = {
                'TimeTableForm[faculty]': item['faculty_id'],
                'TimeTableForm[course]': item['course_id'],
            }
            self.logger.debug('parse group %s', form_data)
            request = http.FormRequest(url=response.url, formdata=form_data, callback=self.parse_group)
            request.meta['item'] = item
            yield request

    def parse_group(self, response):
        """
        Parse id and name of group.
        """
        for group in response.xpath('//*[@id="TimeTableForm_group"]/option')[1:]:
            group_id = group.xpath('@value').get()
            group_name = group.xpath('text()').get()
            if (not group_id) or (not group_name):
                self.logger.debug('Failed to parse id or info for %s group_id %s group_name', group_id, group_name)
                shell.inspect_response(response, self)
                raise exceptions.CloseSpider('')
                continue

            item = response.meta['item']
            item['group_id'] = group_id
            item['group_name'] = group_name
            form_data = {
                'TimeTableForm[faculty]': item['faculty_id'],
                'TimeTableForm[course]': item['course_id'],
                'TimeTableForm[group]': item['group_id'],
            }
            self.logger.debug('parse group %s', form_data)
            # request = http.FormRequest(url=response.url, formdata=form_data, callback=self.parse_schedule)
            # request.meta['item'] = item
            # yield request

    def parse_schedule(self, response):
        """
        Parse actual schedule of group.
        """
        item = response.meta['item']
        table = response.xpath('//*[@id="timeTableGroup"]/tr')

        for row in table:
            # cycle for day of week
            lessons_info = row.xpath('./td/div[@class="mh-50 cell cell-vertical"]/span[1]/text()').getall()
            day_of_week = row.xpath('./td/div/text()').get()
            item['day_of_week'] = day_of_week
            for day in row.xpath('./td')[1:]:
                date = day.xpath('./div/text()').get()
                item['date'] = date
                lessons = day.xpath('./div[@class="cell mh-50"]')
                for index, lesson in enumerate(lessons):
                    item['lesson_number'] = lessons_info[index]
                    lesson_tag_value = lesson.xpath('./@data-content').get()
                    if not lesson_tag_value:
                        self.logger.debug('Skip empty cell for group %s faculcy %s at %s ', item['group_name'],
                                          item['faculty_name'], date)
                        continue
                    lesson = list(filter(None, map(str.strip, lesson_tag_value.split('<br>'))))
                    item['discipline'] = lesson[0]
                    item['audience'] = lesson[1].split('-', 1)[1]
                    item['corpus_number'] = lesson[1].split('-', 1)[0].split('. ', 1)[1]
                    item['lecturer'] = lesson[2]
                    item['added_at'] = lesson[3]
                    yield item
