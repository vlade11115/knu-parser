# -*- coding: utf-8 -*-
from scrapy import Spider, http, shell, loader, selector, exceptions

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
        for faculty in response.xpath('//*[@id="TimeTableForm_faculty"]/option'):
            faculty_id = faculty.xpath('@value').get()
            if not faculty_id:
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
        for course in response.xpath('//*[@id="TimeTableForm_course"]/option'):
            course_id = course.xpath('@value').get()
            if not course_id:
                continue
            item = response.meta['item']
            item['course_id'] = course_id
            form_data = {
                'TimeTableForm[faculty]': item['faculty_id'],
                'TimeTableForm[course]': item['course_id'],
            }

            request = http.FormRequest(url=response.url, formdata=form_data, callback=self.parse_group)
            request.meta['item'] = item
            yield request

    def parse_group(self, response):
        """
        Parse id and name of group.
        """
        for group in response.xpath('//*[@id="TimeTableForm_group"]/option'):
            group_id = group.xpath('@value').get()
            group_name = group.xpath('text()').get()
            if (not group_id) or (not group_name):
                continue

            item = response.meta['item']
            item['group_id'] = group_id
            item['group_name'] = group_name
            form_data = {
                'TimeTableForm[faculty]': item['faculty_id'],
                'TimeTableForm[course]': item['course_id'],
                'TimeTableForm[group]': item['group_id'],
            }
            request = http.FormRequest(url=response.url, formdata=form_data, callback=self.parse_schedule)
            request.meta['item'] = item
            yield request

    def parse_schedule(self, response):
        """
        Parse actual schedule of group.
        """
        item = response.meta['item']
        table = response.xpath('//*[@id="timeTableGroup"]/tr')
        for row in table:
            # cycle for day of week
            day_of_week = row.xpath('./td[1]/div/text()').get()
            item['day_of_week'] = day_of_week
            shell.inspect_response(response, self)
            raise exceptions.CloseSpider('bandwidth_exceeded')
            yield item
