# -*- coding: utf-8 -*-
from scrapy import Spider, FormRequest

from knu_parser.items import KnuParserItem


class ScheduleSpider(Spider):
    name = 'schedule'
    allowed_domains = ['asu.knu.edu.ua']
    start_urls = [
        'http://asu.knu.edu.ua/timeTable/group',
    ]

    def parse(self, response):
        """
        Parse initial page, take faculty id and name.
        """
        for faculty in response.xpath('//*[@id="TimeTableForm_faculty"]/option')[1:]:
            faculty_id = faculty.xpath('@value').get()
            faculty_name = faculty.xpath('text()').get()
            form_data = {'TimeTableForm[faculty]': faculty_id}
            item = KnuParserItem({'faculty_id': faculty_id, 'faculty_name': faculty_name})
            yield FormRequest(url=response.url, formdata=form_data, callback=self.parse_course,
                              meta={'item': item})

    def parse_course(self, response):
        """
        Parse id of course.
        """
        for course_id in response.xpath('//*[@id="TimeTableForm_course"]/option/@value')[1:].getall():
            item = response.meta['item'].copy()
            item['course_id'] = course_id
            form_data = {
                'TimeTableForm[faculty]': item['faculty_id'],
                'TimeTableForm[course]': item['course_id'],
            }
            yield FormRequest(url=response.url, formdata=form_data, callback=self.parse_group, meta={'item': item})

    def parse_group(self, response):
        """
        Parse id and name of group.
        """
        for group in response.xpath('//*[@id="TimeTableForm_group"]/option')[1:]:
            item = response.meta['item'].copy()
            group_id = group.xpath('@value').get()
            group_name = group.xpath('text()').get()

            item['group_id'] = group_id
            item['group_name'] = group_name
            form_data = {
                'TimeTableForm[faculty]': item['faculty_id'],
                'TimeTableForm[course]': item['course_id'],
                'TimeTableForm[group]': item['group_id'],
            }
            yield FormRequest(url=response.url, formdata=form_data, callback=self.parse_schedule,
                              meta={'item': item})

    def parse_schedule(self, response):
        """
        Parse actual schedule of group.
        """
        table = response.xpath('//*[@id="timeTableGroup"]/tr')
        item = response.meta['item'].copy()

        for row in table:
            # cycle for day of week
            lessons_info = row.xpath('./td/div[@class="mh-50 cell cell-vertical"]/span[1]/text()').getall()
            lessons_start = row.xpath(
                './td/div[@class="mh-50 cell cell-vertical"]/span[@class="start"]/text()').getall()
            lessons_finish = row.xpath(
                './td/div[@class="mh-50 cell cell-vertical"]/span[@class="finish"]/text()').getall()
            day_of_week = row.xpath('./td/div/text()').get()
            item['day_of_week'] = day_of_week
            for day in row.xpath('./td')[1:]:
                item['date'] = day.xpath('./div/text()').get()
                lessons = day.xpath('./div[@class="cell mh-50"]')
                if not lessons:
                    self.logger.debug('Skip empty day %s', item)
                    continue
                count = 0
                week_number = 1
                for index, lesson in enumerate(lessons):
                    item['week_number'] = week_number
                    if not (index % len(lessons)):
                        week_number = 2 if week_number == 1 else 1
                    item['lesson_number'] = lessons_info[count].split()[0]
                    item['lesson_start'] = lessons_start[count]
                    item['lesson_finish'] = lessons_finish[count]
                    count += 1
                    if count == len(lessons_info) - 1:
                        count = 0
                    lesson_tag_value = lesson.xpath('./@data-content').get()
                    if not lesson_tag_value:
                        self.logger.debug('Skip empty lesson %s', item)
                        continue
                    lesson = list(filter(None, map(str.strip, lesson_tag_value.split('<br>'))))
                    discipline = lesson[0]
                    item['discipline'] = discipline[:discipline.find('[')]
                    item['lesson_type'] = discipline[discipline.find('[') + 1:discipline.find(']')]
                    item['audience'] = lesson[1].split('-', 1)[1]
                    item['corpus_number'] = lesson[1].split('-', 1)[0].split('. ', 1)[1]
                    item['lecturer'] = lesson[2]
                    yield item
