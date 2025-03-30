box.cfg {}

if not box.space.polls then
    local polls_space = box.schema.space.create('polls')
    polls_space:format({
        {name = 'id', type = 'string'},
        {name = 'data', type = 'any'},
    })
    polls_space:create_index('primary', {parts = {'id'}})
end